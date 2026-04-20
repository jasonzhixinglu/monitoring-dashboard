# Sandbox Workflow: China Activity Charts (Apr 19, 2026)

## Overview
This sandbox session produced three charts analyzing China's March 2026 activity data release (Apr 15-16).

## Workflow Pattern
The session followed an iterative loop:
- **Claude (this chat)**: Design thinking, economic logic, prompt drafting
- **Claude Code (Codespaces)**: Execution, file I/O, data loading, chart rendering
- **Jason (you)**: Design decisions, domain expertise, course corrections

### Where the workflow worked well:
- Claude Code excelled at boilerplate (imports, Plotly setup, file I/O, debugging path issues)
- Claude (chat) good at drafting prompts and economic framing (which series matter for PCA, why FAI YTD is noisy)
- Jason essential for: stopping bad ideas (two-series PCA), pivoting to better data (swap NSA exports for SA), final polish decisions (time window scaling)

### Where it struggled:
- Early series selection: Claude suggested only 3 headlines (IVA, FAI, Retail) without seeing the full data. Jason had to push for the complete list before we realized we needed 4+ indicators for a meaningful PCA.
- Chart output format: No one initially objected to HTML files; needed Jason to point out we wanted static images + 5-year windows.

### Key lesson:
**Show the full data first, then decide.** Claude Code should dump available series early; Claude can then help filter down rather than guessing what's relevant.

## Outputs
- `chart_builder_20260419.py`: Main script (GDP, Activity YoY, Activity PCA)
- `output_20260419/`: Three PNG charts
  - `gdp_chart.png`: Real GDP Q/Q SA and YoY (2021–Apr 2026)
  - `activity_yoy_chart.png`: IVA, Retail, Exports (SA), TSF YoY (2021–Mar 2026)
  - `activity_factor_chart.png`: Common factor across four indicators (PCA)

## Data & Methods
- Source: `haver-data` Parquet (407 series across 8 databases)
- Apr 15-16 release: 22 China series (GDP, activity, employment)
- PCA: Standardized YoY growth rates, four indicators, equal weight
- Time window: 5 years (consistent across all charts)

## Next steps
- Integrate into monitoring dashboard if workflow proves reusable
- Consider promoting chart styling functions to `sandbox/utils.py`
- Archive this session; start new dated session for next data release
