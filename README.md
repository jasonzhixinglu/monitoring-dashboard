# Monitoring dashboard

A Streamlit-based macro monitoring dashboard for China and Japan. Built on top of the [`haver-data`](https://github.com/jasonzhixinglu/haver-data) upstream repo, which supplies the underlying parquet time-series files.

> **PoC Status** — This is an early prototype. Coverage is limited to China and Japan; the factor model is a first-principal-component PCA with no tuning. Treat outputs as directional indicators, not production forecasts.

---

## What it does

The dashboard surfaces three **themes** per country:

| Theme | What it covers |
|---|---|
| **Activity** | Industrial production, retail sales, investment, exports, unemployment |
| **Inflation** | Headline CPI, core CPI, food CPI, services CPI (and energy for Japan) |
| **PMIs** | Manufacturing and services PMI survey readings |

For Activity and Inflation themes the app fits a **dynamic common-factor** (first principal component) that compresses the indicators into a single standardised reading. PMIs are shown as a standardised multi-line chart without a factor model.

### Dashboard layout

Each Activity / Inflation page is a **2 × 2 grid**:

```
┌─────────────────────────┬──────────────────────────┐
│  Factor chart (line)    │  Latest snapshot          │
│  Indicator chart (std)  │  (monospace data table)   │
├─────────────────────────┼──────────────────────────┤
│  Surprise heatmap       │  Contributions (radial)   │
│  (last 24 months)       │  (latest period)          │
└─────────────────────────┴──────────────────────────┘
```

- **Factor chart** — common factor time series (mean 0, std 1)
- **Standardised indicator chart** — each raw indicator z-scored for a comparable scale
- **Latest snapshot** — last available value per series, plus the factor reading
- **Surprise heatmap** — AR(1) one-step-ahead forecast errors per indicator, last 24 months
- **Contributions radial** — each indicator's loading × residual for the latest period
- **Data table + CSV download** — raw transformed values (not standardised) for the last 24 months; full-history CSV available via the download button

---

## Factor model

1. Each indicator is transformed (level / YoY % / MoM %) and then z-scored.
2. Outliers beyond `mean ± 10 × IQR` are winsorised to NaN before PCA.
3. The first principal component is extracted via eigendecomposition of the correlation matrix (listwise deletion for the PCA fit).
4. The factor is re-standardised to mean 0, variance 1.
5. Per-indicator R² and residuals are computed via OLS of each standardised series on the factor.
6. "Surprises" are AR(1) one-step-ahead forecast errors on the residuals.

Indicators flagged `"in_pca": False` appear in charts and get R² / residuals computed against the factor, but do not enter the PCA itself (used for China Real Estate Investment to avoid distorting the common factor with COVID base effects).

---

## Getting started

### Prerequisites

- Python 3.10+
- A local clone of [`haver-data`](https://github.com/jasonzhixinglu/haver-data)

### Install

```bash
git clone https://github.com/jasonzhixinglu/monitoring-dashboard
cd monitoring-dashboard
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501`. Use the sidebar to choose a country and theme.

---

## Data source

The app reads two parquet files from the `haver-data` repo:

```
haver-data/
  data/
    data.parquet      # columns: date, code, value, frequency
    metadata.parquet  # series metadata
```

Series codes use the `name@database` format (e.g. `h924d@emergepr`).

**Default path** — if both repos are cloned side-by-side under `/workspaces/`, no configuration is needed:

```
/workspaces/
  haver-data/
  monitoring-dashboard/
```

**Override** with an environment variable if your layout differs:

```bash
export HAVER_DATA_REPO=/path/to/haver-data
streamlit run app.py
```

The home page (`app.py`) shows live file-existence status and a data preview.

---

## Project structure

```
monitoring-dashboard/
├── app.py                   # Home page — data-source status
├── pages/
│   ├── China.py             # China monitor page
│   └── Japan.py             # Japan monitor page
├── src/
│   ├── monitor_config.py    # Indicator definitions (codes, labels, transforms)
│   ├── data_access.py       # Parquet loaders, path resolution
│   ├── transforms.py        # level / yoy / mom transforms
│   ├── factor_analysis.py   # PCA factor extraction, residuals, surprises
│   ├── charts.py            # Plotly chart builders + table/CSV helpers
│   └── page_utils.py        # Streamlit page rendering logic
├── docs/                    # GitHub Pages static demo
│   ├── index.html           # Landing page
│   └── snapshots/           # Exported static chart HTML files
├── scripts/
│   └── export_snapshot.py   # Generates static HTML snapshots for docs/
├── requirements.txt
└── .gitignore
```

---

## GitHub Pages demo

A static snapshot of the China Activity dashboard is published at:  
**https://jasonzhixinglu.github.io/monitoring-dashboard/**

The snapshot is generated from real data using `scripts/export_snapshot.py`. It is not live-updating — regenerate with:

```bash
python scripts/export_snapshot.py
```

Then commit the updated `docs/` folder and push.

---

## Adding a new country

1. Add a config block in `src/monitor_config.py` following the `CHINA` / `JAPAN` pattern.
2. Create `pages/NewCountry.py` (copy either existing page file, update the import and title).
3. Add the country to `COUNTRIES` dict in `monitor_config.py` if needed.

