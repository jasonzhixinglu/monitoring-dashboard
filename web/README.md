# Monitoring Dashboard — React Web App

Static React/Vite app that replicates the Streamlit monitoring dashboard using pre-computed JSON data.

## Development

```bash
cd web
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Build

```bash
npm run build   # outputs to web/dist/
```

## Updating data

Re-run the Python export script from the project root, then rebuild:

```bash
cd ..
python scripts/export_dashboard_data.py
cd web
npm run build
```

## Structure

- `src/data/` — pre-computed JSON files (one per country/theme)
- `src/components/` — React components
- `src/hooks/useThemeData.ts` — data loading hook
- `src/types/index.ts` — TypeScript interfaces
