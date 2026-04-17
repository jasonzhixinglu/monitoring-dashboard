import io
import pandas as pd
import plotly.graph_objects as go


def _short_label(label: str, max_len: int = 28) -> str:
    """Strip transform tag and truncate for compact axis labels."""
    short = label.split(" [")[0]
    return short[:max_len] if len(short) > max_len else short


# ---------------------------------------------------------------------------
# Factor / data tables
# ---------------------------------------------------------------------------

def factor_data_table_transformed(
    factor_series: pd.Series,
    inputs_df: pd.DataFrame,
    last_n_months: int = 24,
) -> pd.DataFrame:
    """Last N months: factor + raw transformed input values (no standardization, no imputation)."""
    fdf = pd.DataFrame({"date": factor_series.index, "factor": factor_series.values})
    merged = fdf.merge(inputs_df, on="date", how="left")
    merged = merged.dropna(subset=["factor"]).tail(last_n_months).copy()
    merged["date"] = merged["date"].dt.strftime("%Y-%m")
    merged["factor"] = merged["factor"].round(3)
    for col in [c for c in merged.columns if c not in ("date", "factor")]:
        merged[col] = merged[col].round(2)
    return merged.reset_index(drop=True)


def factor_and_inputs_csv(factor_series: pd.Series, transformed_inputs_df: pd.DataFrame) -> bytes:
    """Full history: factor + raw transformed inputs as CSV bytes (no truncation, no imputation)."""
    fdf = pd.DataFrame({"date": factor_series.index, "factor": factor_series.values})
    merged = fdf.merge(transformed_inputs_df, on="date", how="left").copy()
    merged["date"] = merged["date"].dt.strftime("%Y-%m-%d")
    merged["factor"] = merged["factor"].round(3)
    for col in [c for c in merged.columns if c not in ("date", "factor")]:
        merged[col] = merged[col].round(3)
    buf = io.BytesIO()
    merged.to_csv(buf, index=False)
    return buf.getvalue()


def latest_realizations_table(transformed_inputs_df: pd.DataFrame) -> pd.DataFrame:
    """Return [Series Name, Latest Value, Date] using each series' own latest non-NaN."""
    indicator_cols = [c for c in transformed_inputs_df.columns if c != "date"]
    rows = []
    for col in indicator_cols:
        sub = transformed_inputs_df[["date", col]].dropna()
        if sub.empty:
            continue
        last = sub.iloc[-1]
        rows.append({
            "Series": col,
            "Latest Value": round(float(last[col]), 2),
            "Date": last["date"].strftime("%Y-%m"),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def factor_chart(factor_series: pd.Series, title: str = "", height: int = 300) -> go.Figure:
    """Line chart of a standardized factor with a zero reference line."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=factor_series.index,
        y=factor_series.values,
        mode="lines",
        name="Factor",
        line=dict(color="#1f77b4", width=2),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig.update_layout(
        title=title,
        hovermode="x unified",
        yaxis_title="Std Dev",
        showlegend=False,
        height=height,
        margin=dict(t=40, b=30, l=50, r=20),
    )
    return fig


def theme_chart(
    df: pd.DataFrame,
    title: str = "",
    height: int = 300,
    yaxis_title: str = "",
) -> go.Figure:
    """Multi-line chart for a theme DataFrame (date col + one col per indicator)."""
    fig = go.Figure()
    for col in df.columns:
        if col == "date":
            continue
        fig.add_trace(go.Scatter(
            x=df["date"], y=df[col], mode="lines",
            name=_short_label(col),
        ))
    fig.update_layout(
        title=title,
        hovermode="x unified",
        height=height,
        yaxis_title=yaxis_title,
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="left", x=0),
        margin=dict(t=40, b=100, l=50, r=20),
    )
    return fig


def surprise_heatmap(
    surprises_df: pd.DataFrame,
    title: str = "",
    height: int = 380,
    last_n: int = 24,
) -> go.Figure:
    """Heatmap of model surprises: x=date, y=indicator, color=magnitude (diverging RdBu)."""
    recent = surprises_df.dropna(how="all").tail(last_n)
    dates = [d.strftime("%Y-%m") for d in recent.index]
    y_labels = [_short_label(c) for c in recent.columns]
    z = recent.values.T.tolist()

    fig = go.Figure(go.Heatmap(
        z=z,
        x=dates,
        y=y_labels,
        colorscale="RdBu",
        zmid=0,
        colorbar=dict(title="Surprise", thickness=12, len=0.8),
        hoverongaps=False,
    ))
    fig.update_layout(
        title=title,
        height=height,
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=11)),
        margin=dict(t=40, b=60, l=160, r=40),
    )
    return fig


def contributions_radial(
    contributions_dict: dict,
    title: str = "",
    height: int = 380,
) -> go.Figure:
    """Polar bar chart of factor contributions (crimson=positive, steel blue=negative)."""
    indicators = list(contributions_dict.keys())
    values = [contributions_dict[k] for k in indicators]
    labels = [_short_label(ind) for ind in indicators]
    colors = ["crimson" if v >= 0 else "steelblue" for v in values]

    fig = go.Figure(go.Barpolar(
        r=[abs(v) for v in values],
        theta=labels,
        marker_color=colors,
        marker_line_color="white",
        marker_line_width=1,
        opacity=0.85,
    ))
    fig.update_layout(
        title=title,
        height=height,
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False, gridcolor="lightgray"),
            angularaxis=dict(tickfont=dict(size=10)),
        ),
        showlegend=False,
        margin=dict(t=50, b=20, l=40, r=40),
        annotations=[dict(
            text="crimson=↑  blue=↓",
            xref="paper", yref="paper",
            x=0.5, y=-0.02, showarrow=False,
            font=dict(size=10, color="gray"),
        )],
    )
    return fig
