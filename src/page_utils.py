import warnings
import pandas as pd
import streamlit as st

from src.data_access import load_series
from src.transforms import apply_transform
from src.factor_analysis import extract_factor
from src.charts import (
    theme_chart, factor_chart, surprise_heatmap, contributions_radial,
    latest_realizations_table, factor_data_table_transformed, factor_and_inputs_csv,
)

_TRANSFORM_TAG = {"yoy": "YoY", "mom": "MoM", "level": "Level"}
_YEAR_OPTIONS = [2, 3, 5, 10, 15, 20]
_YEAR_DEFAULT_IDX = 3  # 10 years


def display_label(label: str, transform: str) -> str:
    return f"{label} [{_TRANSFORM_TAG.get(transform, transform.upper())}]"


def build_theme_df(indicators: list) -> pd.DataFrame:
    """Load + transform all indicators. Column names include the transform tag."""
    series = {}
    for ind in indicators:
        try:
            s = load_series(ind["code"])
            s = apply_transform(s, ind["transform"])
            series[display_label(ind["label"], ind["transform"])] = s
        except Exception as e:
            warnings.warn(f"Skipping {ind['code']}: {e}")
    if not series:
        return pd.DataFrame()
    df = pd.DataFrame(series)
    df.index.name = "date"
    return df.reset_index()


def standardize_dataframe(df: pd.DataFrame, exclude_cols: list = None) -> pd.DataFrame:
    """Z-score each column not in exclude_cols. NaN rows preserved."""
    exclude = set(exclude_cols or ["date"])
    result = df.copy()
    for col in df.columns:
        if col in exclude:
            continue
        mu, sigma = df[col].mean(), df[col].std()
        result[col] = (df[col] - mu) / sigma if sigma > 1e-12 else 0.0
    return result


def compute_contributions(loadings: dict, residuals_row: pd.Series) -> dict:
    """Contribution of each indicator to current factor = loading × latest residual."""
    result = {}
    for ind, loading in loadings.items():
        val = residuals_row.get(ind, float("nan"))
        if pd.notna(val):
            result[ind] = float(loading * val)
    return result


def format_latest_snapshot(
    transformed_inputs_df: pd.DataFrame,
    factor_series: pd.Series,
    latest_date: pd.Timestamp,
) -> str:
    """Monospace snapshot: Series Name | Latest Value, plus the factor reading."""
    header = f"Latest Data (as of {latest_date.strftime('%Y-%m-%d')})"
    sep = "─" * 52
    col_w = 40
    lines = [header, sep, f"{'Series':<{col_w}} {'Value':>10}", sep]

    indicator_cols = [c for c in transformed_inputs_df.columns if c != "date"]
    for col in indicator_cols:
        sub = transformed_inputs_df[["date", col]].dropna()
        if sub.empty:
            continue
        val = sub.iloc[-1][col]
        lines.append(f"{col:<{col_w}} {round(float(val), 2):>10}")

    latest_factor = factor_series.dropna().iloc[-1]
    lines.append(sep)
    lines.append(f"{'Common Factor':<{col_w}} {latest_factor:>10.3f}")
    return "\n".join(lines)


def model_diagnostics_text(loadings: dict, r_squared: dict) -> str:
    """Monospace-formatted diagnostics table: Series | R² | Loading."""
    header = f"{'Series':<46} {'R²':>6}  {'Loading':>7}"
    sep = "─" * len(header)
    lines = [header, sep]
    for k, loading in loadings.items():
        r2 = r_squared.get(k, "—")
        r2_str = f"{r2:.3f}" if isinstance(r2, float) else r2
        lines.append(f"{k:<46} {r2_str:>6}  {loading:>7.3f}")
    return "\n".join(lines)


def _cutoff(df: pd.DataFrame, years: int) -> pd.Timestamp:
    indicator_cols = [c for c in df.columns if c != "date"]
    latest = df.dropna(subset=indicator_cols, how="all")["date"].max()
    return latest - pd.DateOffset(years=years)


def render_country_page(country: str, config: dict) -> None:
    """Main entry point for a country page."""
    theme_label = st.sidebar.selectbox(
        "Select theme", ["Activity", "Inflation", "PMIs"],
        key=f"{country}_theme",
    )
    years = st.sidebar.selectbox(
        "Show last ___ years", _YEAR_OPTIONS, index=_YEAR_DEFAULT_IDX,
        key=f"{country}_years",
    )

    theme_key = theme_label.lower()
    indicators = config[theme_key]

    df = build_theme_df(indicators)
    if df.empty:
        st.warning("No data available.")
        return

    cutoff = _cutoff(df, years)

    if theme_key == "pmis":
        _render_pmi_section(country, df, cutoff)
    else:
        remove_outliers = st.sidebar.toggle(
            "Remove outliers", value=True, key=f"{country}_ro"
        )
        _render_indicator_section(
            country, theme_key, indicators, df, cutoff, remove_outliers
        )


def _render_pmi_section(country: str, df: pd.DataFrame, cutoff: pd.Timestamp) -> None:
    df_std = standardize_dataframe(df)
    df_win = df_std[df_std["date"] >= cutoff]

    col_chart, col_tbl = st.columns(2)
    with col_chart:
        st.plotly_chart(
            theme_chart(df_win, title=f"{country} — PMIs", yaxis_title="Std Dev"),
            use_container_width=True,
        )
    with col_tbl:
        st.caption("Latest PMI readings")
        st.dataframe(
            latest_realizations_table(df),
            hide_index=True, use_container_width=True,
        )


def _render_indicator_section(
    country: str,
    theme: str,
    indicators: list,
    df: pd.DataFrame,
    cutoff: pd.Timestamp,
    remove_outliers: bool,
) -> None:
    df_std = standardize_dataframe(df)
    df_win = df_std[df_std["date"] >= cutoff]

    pca_cols = [
        display_label(ind["label"], ind["transform"])
        for ind in indicators if ind.get("in_pca", True)
    ]
    try:
        result = extract_factor(df, remove_outliers_flag=remove_outliers, pca_cols=pca_cols)
    except ValueError as e:
        # Fall back to chart + table without factor
        st.plotly_chart(
            theme_chart(df_win, title=f"{country} — {theme.title()} (standardized)", yaxis_title="Std Dev"),
            use_container_width=True,
        )
        st.warning(f"Factor extraction skipped: {e}")
        return

    factor = result["factor"]
    factor_win = factor[factor.index >= cutoff]
    indicator_cols = [c for c in df.columns if c != "date"]
    latest_date = df.dropna(subset=indicator_cols, how="all")["date"].max()

    # ── Top row: charts left | snapshot right ────────────────────────────────
    col_charts, col_info = st.columns(2)

    with col_charts:
        st.plotly_chart(
            factor_chart(factor_win, title="Common Factor"),
            use_container_width=True,
        )
        st.plotly_chart(
            theme_chart(df_win, title="Standardized Indicators", yaxis_title="Std Dev"),
            use_container_width=True,
        )

    with col_info:
        st.code(format_latest_snapshot(df, factor, latest_date))

    # ── Bottom row: heatmap left | radial right ──────────────────────────────
    col_heat, col_rad = st.columns(2)

    with col_heat:
        st.plotly_chart(
            surprise_heatmap(result["surprises"], title="Surprises (last 24 months)"),
            use_container_width=True,
        )

    with col_rad:
        latest_resid = result["residuals"].dropna(how="all").iloc[-1]
        contribs = compute_contributions(result["loadings"], latest_resid)
        if contribs:
            st.plotly_chart(
                contributions_radial(contribs, title="Factor Contributions (latest)"),
                use_container_width=True,
            )
        else:
            st.info("No contributions available for the latest period.")

    st.divider()

    # ── Data table + download ────────────────────────────────────────────────
    tbl = factor_data_table_transformed(factor, df, last_n_months=24)
    st.caption("Factor + transformed inputs — last 24 months (raw, no standardization)")
    st.dataframe(tbl, hide_index=True, use_container_width=True)
    st.download_button(
        "Download factor + inputs (full history, CSV)",
        data=factor_and_inputs_csv(factor, df),
        file_name=f"{country.lower()}_{theme}_factor_and_inputs.csv",
        mime="text/csv",
        key=f"{country}_{theme}_dl",
    )

    # ── Diagnostics expander ─────────────────────────────────────────────────
    with st.expander("Model diagnostics"):
        st.code(model_diagnostics_text(result["loadings"], result["r_squared"]))
