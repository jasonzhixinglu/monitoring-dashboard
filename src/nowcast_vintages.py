"""Pseudo-vintage nowcasts for Q1 2026, week by week."""

import warnings
from datetime import date, timedelta

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from statsmodels.tsa.statespace.dynamic_factor_mq import DynamicFactorMQ

from src.data_access import load_series
from src.nowcast_config import NOWCAST_COUNTRIES
from src.transforms import apply_transform


def _released_by(vintage: date, period: pd.Period, release_day: int) -> bool:
    """True if data for `period` (monthly) would be available on `vintage`.

    Convention: data for month M releases in month M+1 on `release_day`.
    """
    next_month = date(period.year, period.month, 1) + relativedelta(months=1)
    release = next_month.replace(day=min(release_day, 28))
    return vintage >= release


def build_pseudo_vintages(
    country: str,
    nowcast_quarter: str = "2026Q1",
    estimation_start: str = "2006-01-01",
) -> pd.DataFrame:
    """Return weekly pseudo-vintage nowcasts for the target quarter.

    Parameters
    ----------
    country : "US" or "Japan"
    nowcast_quarter : target quarter, e.g. "2026Q1"
    estimation_start : start of estimation window

    Returns
    -------
    DataFrame with columns [vintage_date (str), nowcast_value (float|None)]
    """
    config = NOWCAST_COUNTRIES[country]
    target_cfg = config["target"]
    indicators = [ind for ind in config["indicators"] if ind.get("in_model", True)]
    pre_transformed = target_cfg.get("pre_transformed", False)

    # ── Load all data once ──────────────────────────────────────────────────
    gdp_raw = load_series(target_cfg["code"])
    gdp_growth = gdp_raw.copy() if pre_transformed else apply_transform(gdp_raw, "qoqar")
    gdp_growth = gdp_growth[gdp_growth.index >= estimation_start]
    gdp_q = pd.Series(
        gdp_growth.values,
        index=pd.PeriodIndex(gdp_growth.index, freq="Q"),
        name="GDP Growth",
    )

    series_cache: list[tuple[str, pd.Series, int]] = []
    for ind in indicators:
        try:
            s = load_series(ind["code"])
            s = apply_transform(s, ind["transform"])
            s = s[s.index >= estimation_start]
            s_m = pd.Series(s.values, index=pd.PeriodIndex(s.index, freq="M"), name=ind["label"])
            series_cache.append((ind["label"], s_m, ind["release_day"]))
        except Exception as e:
            warnings.warn(f"Skipping {ind['code']}: {e}")

    # ── Build full panel (extended to Q1 2026) ──────────────────────────────
    target_end_m = pd.Period(
        pd.Period(nowcast_quarter, freq="Q").to_timestamp(how="end"), freq="M"
    )

    def _make_panel(label_series: list[tuple[str, pd.Series]]) -> pd.DataFrame:
        cols = {lbl: s for lbl, s in label_series}
        panel = pd.DataFrame(cols)
        if panel.index.max() < target_end_m:
            extra = pd.period_range(panel.index.max() + 1, target_end_m, freq="M")
            panel = pd.concat([panel, pd.DataFrame(index=extra, columns=panel.columns)])
        return panel

    full_panel = _make_panel([(lbl, s) for lbl, s, _ in series_cache])

    # ── Fit full-sample model (parameters fixed for all vintages) ──────────
    q1 = pd.Period(nowcast_quarter, freq="Q")
    gdp_q_fit = gdp_q.copy()
    if q1 in gdp_q_fit.index:
        gdp_q_fit.loc[q1] = np.nan  # Q1 2026 is always the nowcast target

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mod_full = DynamicFactorMQ(
            endog=full_panel,
            endog_quarterly=gdp_q_fit.to_frame(),
            factors=2,
            factor_orders=2,
            idiosyncratic_ar1=True,
        )
        try:
            res_full = mod_full.fit(disp=False, maxiter=200)
        except Exception:
            res_full = mod_full.fit_em(maxiter=200, disp=False)

    # ── Weekly vintage loop ─────────────────────────────────────────────────
    start = date(2026, 1, 5)  # first Monday of January 2026
    today = date.today()
    vintage_dates = [start + timedelta(weeks=k) for k in range(((today - start).days // 7) + 1)]

    # Q1 months that we're waiting to be released
    q1_months = [pd.Period("2026-01", freq="M"),
                 pd.Period("2026-02", freq="M"),
                 pd.Period("2026-03", freq="M")]

    records = []
    for vd in vintage_dates:
        # Has any Q1 indicator data been released yet?
        has_q1_data = any(
            _released_by(vd, m, rd)
            for _, _, rd in series_cache
            for m in q1_months
        )

        if not has_q1_data:
            records.append({"vintage_date": str(vd), "nowcast_value": None})
            continue

        # Mask unreleased monthly observations
        masked = full_panel.copy()
        for lbl, _, rd in series_cache:
            if lbl not in masked.columns:
                continue
            for period in masked.index:
                if not _released_by(vd, period, rd):
                    masked.loc[period, lbl] = np.nan

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # apply() re-uses fitted params from full-sample model on new data
                res_v = res_full.apply(masked, endog_quarterly=gdp_q_fit.to_frame())
                pred = res_v.predict()
                gdp_col = pred["GDP Growth"] if "GDP Growth" in pred.columns else pd.Series(dtype=float)
                q1_vals = [
                    float(gdp_col[gdp_col.index == m].iloc[0])
                    for m in q1_months
                    if m in gdp_col.index and not np.isnan(float(gdp_col[gdp_col.index == m].iloc[0]))
                ]
                val = float(np.mean(q1_vals)) if q1_vals else None
        except Exception as e:
            warnings.warn(f"Vintage {vd} failed: {e}")
            val = None

        records.append({"vintage_date": str(vd), "nowcast_value": val})

    return pd.DataFrame(records)
