# Monitoring & Nowcasting Dashboard

A React-based macro monitoring and GDP nowcasting dashboard for China, Japan, and the US. Built on top of the [`haver-data`](https://github.com/jasonzhixinglu/haver-data) upstream repo, which supplies the underlying parquet time-series files.

**Live:** https://jasonzhixinglu.github.io/monitoring-dashboard/

---

## Overview

Two components:

- **Monitoring** — Activity, Inflation, and PMI dashboards for China and Japan. PCA-based common factor with surprise heatmap and radial contributions chart.
- **Nowcasting** — GDP nowcast (Q/Q annualised rate) for the US and Japan. Dynamic Factor Model (DFM) with pseudo-vintage evolution, surprise heatmap, and factor contributions.

---

## Repo structure

```
monitoring-dashboard/
├── src/                          # shared Python logic
│   ├── data_access.py            # loads parquet from haver-data
│   ├── transforms.py             # level, yoy, mom, 3m3mar, qoqar
│   ├── factor_analysis.py        # PCA-based common factor
│   ├── monitor_config.py         # monitoring indicator config
│   ├── nowcast_config.py         # nowcast panel config + DEFAULT_ESTIMATION_START
│   ├── nowcast_model.py          # DynamicFactorMQ model
│   └── nowcast_vintages.py       # pseudo-vintage construction
├── scripts/
│   ├── export_dashboard_data.py  # export monitoring JSON
│   └── export_nowcast_data.py    # export nowcast JSON
├── web/                          # React/Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChartGrid.tsx
│   │   │   ├── LatestSnapshot.tsx
│   │   │   ├── ModelDiagnostics.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ThemePage.tsx
│   │   │   └── nowcast/          # nowcast-specific components
│   │   │       ├── NowcastPage.tsx
│   │   │       ├── GDPChart.tsx
│   │   │       └── VintageChart.tsx
│   │   ├── data/                 # exported JSON files
│   │   ├── hooks/
│   │   │   ├── useThemeData.ts
│   │   │   └── useNowcastData.ts
│   │   └── types/index.ts
│   └── package.json
├── docs/                         # GitHub Pages static build
└── haver-data/                   # upstream data repo (sibling dir)
```

---

## Data pipeline

```
haver-data (parquet) → src/ (Python) → scripts/export_*.py → web/src/data/ (JSON) → React app
```

---

## Getting started

**Prerequisites:** Python 3.11+, Node 18+, `haver-data` cloned alongside this repo.

```bash
# Install Python dependencies
pip install -r requirements.txt

# Export monitoring data (China, Japan × Activity/Inflation/PMIs)
python scripts/export_dashboard_data.py

# Export nowcast data (US, Japan GDP)
python scripts/export_nowcast_data.py

# Run React app locally
cd web && npm install && npm run dev
```

---

## Updating data

```bash
# Pull latest haver-data
cd ../haver-data && git pull && cd ../monitoring-dashboard

# Regenerate all JSON
python scripts/export_dashboard_data.py
python scripts/export_nowcast_data.py

# Rebuild and deploy
cd web && npm run build && cd ..
cp -r web/dist/* docs/
git add docs/ web/src/data/
git commit -m "Update data $(date +%Y-%m-%d)"
git push
```

---

## Adding a new country

- **Monitoring:** add config to `src/monitor_config.py`, add export entry in `scripts/export_dashboard_data.py`, add country to Sidebar.tsx `Country` type.
- **Nowcasting:** add config to `src/nowcast_config.py`, add country to Sidebar.tsx `NowcastCountry` type. The export script iterates `NOWCAST_COUNTRIES` automatically.

---

## GitHub Pages

- Live at: https://jasonzhixinglu.github.io/monitoring-dashboard/
- Built from the `docs/` directory on the `main` branch.
- Update by rerunning export scripts + `npm run build` + copying `web/dist/*` to `docs/` + pushing.

---

## Known limitations

- **Data vintage:** snapshots reflect the export date, not real-time feeds.
- **Pseudo-vintages:** extrapolated from assumed fixed release dates, not real-time data releases.
- **Japan GDP:** `jsngpcp@japan` is already in SAAR Q/Q % change format — no transformation applied.
- **Low R² on sentiment indicators** (Consumer Confidence, PMIs) is expected; these series have low factor loading.
- **Estimation window:** 20 years (from 2006-01-01) for nowcast models.
