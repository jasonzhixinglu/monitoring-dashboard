#!/usr/bin/env python3
"""Export nowcast results for US and Japan to JSON for the web dashboard."""

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# Ensure repo root on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.nowcast_config import NOWCAST_COUNTRIES
from src.nowcast_model import run_nowcast
from src.nowcast_vintages import build_pseudo_vintages

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "web" / "src" / "data"


def _safe_float(v):
    if v is None:
        return None
    try:
        f = float(v)
        return None if (np.isnan(f) or np.isinf(f)) else round(f, 4)
    except (TypeError, ValueError):
        return None


def _series_to_json(s: pd.Series) -> dict:
    dates, values = [], []
    for idx, val in s.items():
        dates.append(str(idx)[:10])
        values.append(_safe_float(val))
    return {"dates": dates, "values": values}


def _df_to_series_dict(df: pd.DataFrame) -> dict:
    out = {}
    for col in df.columns:
        col_data = df[col]
        dates = [str(i)[:10] for i in col_data.index]
        values = [_safe_float(v) for v in col_data]
        out[str(col)] = {"dates": dates, "values": values}
    return out


def export_country(country: str) -> dict:
    print(f"\n{'='*60}")
    print(f"  {country}: fitting nowcast model...")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = run_nowcast(country)

    nv = _safe_float(result["nowcast_value"])
    ci = result["nowcast_ci"]
    ci_json = [_safe_float(ci[0]), _safe_float(ci[1])]

    print(f"  Nowcast Q1 2026: {nv:.2f}% [{ci_json[0]:.2f}, {ci_json[1]:.2f}]")
    print(f"  Latest data: {result['latest_data_date']}")

    print(f"  Building pseudo-vintages...")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        vintages_df = build_pseudo_vintages(country)

    v_dates = vintages_df["vintage_date"].tolist()
    v_values = [_safe_float(v) for v in vintages_df["nowcast_value"]]
    print(f"  Vintages: {len(v_dates)} weeks, first non-null: "
          f"{next((v_values[i] for i in range(len(v_values)) if v_values[i] is not None), None)}")

    # Target history
    hist = result["target_history"].dropna()
    hist_json = _series_to_json(hist)

    # Transforms map: indicator label → tag string for display
    _TAG = {"level": "Level", "yoy": "YoY", "mom": "MoM", "3m3mar": "3m3mar", "qoqar": "QOQAR"}
    config = NOWCAST_COUNTRIES[country]
    transforms_json = {
        ind["label"]: _TAG.get(ind["transform"], ind["transform"])
        for ind in config["indicators"]
        if ind.get("in_model", True)
    }

    # Input data (monthly indicators, transformed)
    input_df = result["input_data"]
    input_json = {}
    for col in input_df.columns:
        s = input_df[col].dropna()
        input_json[col] = {"dates": [str(i)[:10] for i in s.index], "values": [_safe_float(v) for v in s]}

    # Surprises = residuals (same structure)
    try:
        resid_df = result["residuals"].dropna(how="all")
        surprises_json = {col: {"dates": [str(i)[:10] for i in resid_df[col].dropna().index],
                                 "values": [_safe_float(v) for v in resid_df[col].dropna()]}
                          for col in resid_df.columns}
    except Exception:
        surprises_json = {}

    # Contributions: loading * Q1-2026 factor mean (factor_df has PeriodIndex)
    contributions = {}
    try:
        loadings = result["loadings"]
        factor_df = result["factor"]
        q1_start = pd.Period("2026-01", freq="M")
        q1_factors = factor_df[factor_df.index >= q1_start]
        if not q1_factors.empty:
            f_mean = q1_factors.mean()
            # factor_df columns may be '0'/'1' strings; use positional access
            f1_val = float(f_mean.iloc[0])
            f2_val = float(f_mean.iloc[1]) if len(f_mean) > 1 else 0.0
            for lbl in loadings.index:
                row = loadings.loc[lbl]
                contrib = float(row.get("Factor 1", 0) * f1_val +
                                row.get("Factor 2", 0) * f2_val)
                contributions[lbl] = _safe_float(contrib)
    except Exception as e:
        print(f"  Warning: contributions failed: {e}")

    # Loadings
    loadings_json = {}
    try:
        for lbl in result["loadings"].index:
            row = result["loadings"].loc[lbl]
            loadings_json[lbl] = [_safe_float(row.get("Factor 1")), _safe_float(row.get("Factor 2"))]
    except Exception:
        pass

    # R²
    rsq_json = {k: _safe_float(v) for k, v in result.get("r_squared", {}).items()}

    print(f"  R² per indicator:")
    for k, v in rsq_json.items():
        print(f"    {k:<30} {v}")

    payload = {
        "country": country,
        "nowcast_quarter": "Q1 2026",
        "vintage_date": str(pd.Timestamp.today().date()),
        "nowcast_value": nv,
        "nowcast_ci": ci_json,
        "target_history": hist_json,
        "pseudo_vintages": {
            "dates": v_dates,
            "values": v_values,
        },
        "input_data": input_json,
        "transforms": transforms_json,
        "surprises": surprises_json,
        "contributions": contributions,
        "loadings": loadings_json,
        "r_squared": rsq_json,
    }

    return payload


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for country in NOWCAST_COUNTRIES:
        try:
            payload = export_country(country)
        except Exception as e:
            print(f"ERROR for {country}: {e}")
            import traceback
            traceback.print_exc()
            continue

        fname = f"{country.lower()}_nowcast.json"
        out_path = OUTPUT_DIR / fname
        with open(out_path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"  Written: {out_path}")

        # Validate JSON
        with open(out_path) as f:
            json.load(f)
        print(f"  JSON validation: OK")

    print("\nDone.")


if __name__ == "__main__":
    main()
