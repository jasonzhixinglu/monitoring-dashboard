"""Export dashboard data as JSON files for the React web app.

Usage:
    cd monitoring-dashboard
    python scripts/export_dashboard_data.py
"""

import json
import math
import sys
import warnings
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_access import load_series
from src.transforms import apply_transform
from src.factor_analysis import extract_factor
from src.monitor_config import COUNTRIES

OUTPUT_DIR = Path(__file__).parent.parent / "web" / "src" / "data"

_TRANSFORM_TAG = {"yoy": "YoY", "mom": "MoM", "level": "Level"}


def display_label(label: str, transform: str) -> str:
    tag = _TRANSFORM_TAG.get(transform, transform.upper())
    return f"{label} [{tag}]"


def _to_json_value(v):
    if v is None:
        return None
    try:
        if math.isnan(v) or math.isinf(v):
            return None
    except TypeError:
        pass
    return v


def _series_to_list(s: pd.Series) -> list:
    return [_to_json_value(v) for v in s.tolist()]


def _latest_date(s: pd.Series) -> str:
    """Return the date of the last non-null value as YYYY-MM-DD."""
    valid = s.dropna()
    if valid.empty:
        return ""
    return valid.index[-1].strftime("%Y-%m-%d")


def build_theme_df(indicators: list) -> pd.DataFrame:
    """Load and transform all indicators; returns date-indexed DataFrame."""
    series = {}
    for ind in indicators:
        try:
            s = load_series(ind["code"])
            s = apply_transform(s, ind["transform"])
            series[display_label(ind["label"], ind["transform"])] = s
        except Exception as e:
            warnings.warn(f"  Skipping {ind['code']}: {e}")
    if not series:
        return pd.DataFrame()
    df = pd.DataFrame(series)
    df.index.name = "date"
    return df.reset_index()


def export_theme(country: str, theme: str, indicators: list, vintage: str) -> dict:
    """Build and return the JSON payload for one country/theme combo."""
    df = build_theme_df(indicators)
    if df.empty:
        raise RuntimeError("No data loaded for any indicator.")

    dates = [d.strftime("%Y-%m-%d") for d in df["date"]]
    indicator_cols = [c for c in df.columns if c != "date"]

    inputs = {}
    for col in indicator_cols:
        s = df.set_index("date")[col]
        inputs[col] = {
            "values": _series_to_list(df[col]),
            "latest_date": _latest_date(s),
        }

    payload: dict = {
        "country": country,
        "theme": theme,
        "vintage": vintage,
        "dates": dates,
        "inputs": inputs,
    }

    if theme != "pmis":
        pca_cols = [
            display_label(ind["label"], ind["transform"])
            for ind in indicators if ind.get("in_pca", True)
        ]
        result = extract_factor(df, remove_outliers_flag=True, pca_cols=pca_cols)
        factor_series = result["factor"].reindex(df["date"].values)
        payload["factor"] = {
            "values": _series_to_list(factor_series),
            "latest_date": _latest_date(factor_series.dropna()),
        }
        payload["diagnostics"] = {
            "loadings": {k: round(v, 6) for k, v in result["loadings"].items()},
            "r_squared": {k: round(v, 6) for k, v in result["r_squared"].items()},
        }

    return payload


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    vintage = date.today().strftime("%Y-%m-%d")

    success_count = 0
    sample_payload = None
    sample_label = None

    for country, themes in COUNTRIES.items():
        for theme, indicators in themes.items():
            label = f"{country}/{theme}"
            print(f"Processing {label}...")
            try:
                payload = export_theme(country, theme, indicators, vintage)
            except Exception as e:
                print(f"  ERROR: {e}")
                continue

            out_path = OUTPUT_DIR / f"{country.lower()}_{theme}.json"
            with open(out_path, "w") as f:
                json.dump(payload, f, indent=2)

            n_dates = len(payload["dates"])
            has_factor = "factor" in payload
            print(f"  -> {out_path.name} ({n_dates} dates, factor={'yes' if has_factor else 'no'})")
            success_count += 1

            if sample_payload is None:
                sample_payload = payload
                sample_label = label

    print(f"\nDone: {success_count}/6 files exported to {OUTPUT_DIR}")

    if sample_payload:
        print(f"\nSample (first 3 dates) from {sample_label}:")
        preview: dict = {
            "country": sample_payload["country"],
            "theme": sample_payload["theme"],
            "vintage": sample_payload["vintage"],
            "dates": sample_payload["dates"][:3],
        }
        if "factor" in sample_payload:
            f = sample_payload["factor"]
            preview["factor"] = {"values": f["values"][:3], "latest_date": f["latest_date"]}
        preview["inputs"] = {
            k: {"values": v["values"][:3], "latest_date": v["latest_date"]}
            for k, v in list(sample_payload["inputs"].items())[:2]
        }
        if "diagnostics" in sample_payload:
            preview["diagnostics"] = sample_payload["diagnostics"]
        print(json.dumps(preview, indent=2))


if __name__ == "__main__":
    main()
