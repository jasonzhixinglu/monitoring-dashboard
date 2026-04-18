"""DFM nowcasting model using statsmodels DynamicFactorMQ."""

import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.dynamic_factor_mq import DynamicFactorMQ

from src.data_access import load_series
from src.nowcast_config import NOWCAST_COUNTRIES
from src.transforms import apply_transform


def _to_monthly_period(s: pd.Series) -> pd.Series:
    s = s.copy()
    s.index = pd.PeriodIndex(s.index, freq="M")
    return s


def _to_quarterly_period(s: pd.Series) -> pd.Series:
    s = s.copy()
    s.index = pd.PeriodIndex(s.index, freq="Q")
    return s


def _build_monthly_panel(
    indicators: list[dict],
    estimation_start: str,
    target_end_m: pd.Period,
) -> pd.DataFrame:
    """Load, transform, and assemble the monthly indicator panel."""
    cols = {}
    for ind in indicators:
        if not ind.get("in_model", True):
            continue
        try:
            s = load_series(ind["code"])
            s = apply_transform(s, ind["transform"])
            s = s[s.index >= estimation_start]
            cols[ind["label"]] = _to_monthly_period(s)
        except Exception as e:
            warnings.warn(f"Skipping {ind['code']}: {e}")

    panel = pd.DataFrame(cols)

    # Extend through the end of the nowcast quarter
    if panel.index.max() < target_end_m:
        extra = pd.period_range(panel.index.max() + 1, target_end_m, freq="M")
        panel = pd.concat([panel, pd.DataFrame(index=extra, columns=panel.columns)])

    return panel


def _fit_model(panel_m: pd.DataFrame, gdp_q: pd.Series) -> object:
    """Fit DynamicFactorMQ; fall back to EM if gradient optimisation fails."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mod = DynamicFactorMQ(
            endog=panel_m,
            endog_quarterly=gdp_q.to_frame(),
            factors=2,
            factor_orders=2,
            idiosyncratic_ar1=True,
        )
        try:
            return mod.fit(disp=False, maxiter=200)
        except Exception:
            return mod.fit_em(maxiter=200, disp=False)


def _extract_loadings(res) -> pd.DataFrame:
    """Parse loading parameters from result into a (n_indicators x 2) DataFrame."""
    rows = {}
    for name, val in zip(res.param_names, res.params):
        if not name.startswith("loading."):
            continue
        # Pattern: "loading.{factor_idx}->{label}"
        parts = name[len("loading."):].split("->", 1)
        if len(parts) != 2:
            continue
        factor_idx, label = parts
        rows.setdefault(label, {})[f"Factor {int(factor_idx) + 1}"] = float(val)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).T.rename_axis(None)


def _q1_2026_nowcast(pred: pd.DataFrame) -> tuple[float, float]:
    """Return (nowcast_mean, nowcast_std) for Q1 2026 from monthly GDP predictions.

    DynamicFactorMQ predicts monthly GDP values; Q1 2026 = average of Jan/Feb/Mar.
    """
    gdp_pred = pred["GDP Growth"]
    q1_months = [pd.Period(m, freq="M") for m in ("2026-01", "2026-02", "2026-03")]
    vals = [float(gdp_pred[gdp_pred.index == p].iloc[0])
            for p in q1_months if p in gdp_pred.index and not np.isnan(float(gdp_pred[gdp_pred.index == p].iloc[0]))]
    if not vals:
        return float("nan"), float("nan")
    return float(np.mean(vals)), float(np.std(vals))


def run_nowcast(
    country: str,
    estimation_start: str = "2006-01-01",
) -> dict:
    """Fit a DFM and return nowcast results for Q1 2026.

    Returns
    -------
    dict with keys: nowcast_value, nowcast_ci, nowcast_quarter, factor,
    fitted, residuals, loadings, input_data, target_history,
    estimation_start, latest_data_date, r_squared, model_result.
    """
    config = NOWCAST_COUNTRIES[country]
    target_cfg = config["target"]
    indicators = config["indicators"]
    pre_transformed = target_cfg.get("pre_transformed", False)

    # --- Load and transform GDP ---
    gdp_raw = load_series(target_cfg["code"])
    gdp_growth = gdp_raw.copy() if pre_transformed else apply_transform(gdp_raw, "qoqar")
    gdp_growth = gdp_growth[gdp_growth.index >= estimation_start]
    gdp_q = _to_quarterly_period(gdp_growth)
    gdp_q.name = "GDP Growth"

    # --- Build monthly panel ---
    target_end_m = pd.Period(
        pd.Period("2026Q1", freq="Q").to_timestamp(how="end"), freq="M"
    )
    panel_m = _build_monthly_panel(indicators, estimation_start, target_end_m)

    # --- Fit model ---
    res = _fit_model(panel_m, gdp_q)

    # --- Nowcast Q1 2026 ---
    pred = res.predict()
    nowcast_mean, nowcast_std = _q1_2026_nowcast(pred)

    # 95% CI: ±1.96 * in-sample RMSE as a fallback when std is near zero
    gdp_in_sample = pred["GDP Growth"].dropna()
    actual_q = gdp_q.reindex(gdp_in_sample.index).dropna()
    fit_q = gdp_in_sample.reindex(actual_q.index).dropna()
    rmse = float(np.sqrt(np.mean((fit_q.values - actual_q.values) ** 2))) if len(fit_q) > 0 else 1.0
    nowcast_ci = (nowcast_mean - 1.96 * rmse, nowcast_mean + 1.96 * rmse)

    # --- Factors (smoothed) ---
    factor_df = res.factors["smoothed"].rename(columns={0: "Factor 1", 1: "Factor 2"})
    factor_df.index.name = "date"

    # --- Loadings ---
    loadings = _extract_loadings(res)

    # --- R² (coefficients of determination per factor, summed) ---
    try:
        cod = res.get_coefficients_of_determination()
        r_squared = {lbl: float(cod.loc[lbl].sum()) for lbl in cod.index if lbl != "GDP Growth"}
    except Exception:
        r_squared = {}

    # --- Input data (wide, Timestamp index) ---
    input_wide = panel_m.copy()
    input_wide.index = input_wide.index.to_timestamp()

    latest_data_date = panel_m.dropna(how="all").index.max()

    return {
        "nowcast_value": nowcast_mean,
        "nowcast_ci": nowcast_ci,
        "nowcast_quarter": "Q1 2026",
        "factor": factor_df,
        "fitted": res.fittedvalues,
        "residuals": res.resid,
        "loadings": loadings,
        "input_data": input_wide,
        "target_history": gdp_growth,
        "estimation_start": estimation_start,
        "latest_data_date": str(latest_data_date),
        "r_squared": r_squared,
        "model_result": res,
    }
