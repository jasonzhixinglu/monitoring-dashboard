# Sandbox: Exploratory Chart Work

This directory is a sandpit for experimental chart production on recent China data releases. Charts are built iteratively through discussion between this chat interface and Claude Code in Codespaces.

## Structure

- `chart_builder_YYYYMMDD.py` — dated scripts for each data release session
- `output_YYYYMMDD/` — PNG charts from that session
- `WORKFLOW_LOG_YYYYMMDD.md` — notes on the workflow, decisions, and lessons learned
- `utils.py` — reusable functions promoted from successful experiments

## Workflow

1. **Discovery**: Identify recent China data releases via `haver-data` metadata
2. **Design**: Discuss chart approach here; Claude Code executes and feeds back data
3. **Iteration**: Refine series selection, transforms, and styling based on outputs
4. **Polish**: Jason steps in on design decisions (axis scaling, time windows, indicator selection)
5. **Archive**: Date the script and outputs; document lessons in WORKFLOW_LOG

## Current Session

**2026-04-19**: China activity and GDP charts for Mar 2026 release (Apr 15-16)
- 3 charts: GDP context, activity YoY trends, common factor (PCA)
- See `WORKFLOW_LOG_20260419.md` for details and lessons learned
