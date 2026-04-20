# Sandbox: Exploratory Chart Work

This directory is a sandpit for rapid experimentation on recent macroeconomic data releases. The workflow pairs iterative discussion (Claude.ai chat) with execution (Claude Code in Codespaces) to prototype charts before potential integration into the monitoring dashboard.

## Workflow Overview

**Three roles:**
- **Claude (chat)**: Economic logic, prompt drafting, design thinking
- **Claude Code (Codespaces)**: Execution, file I/O, data loading, debugging
- **Jason (you)**: Domain expertise, course corrections, final design decisions

**Typical cycle:**
1. Identify recent data release via `haver-data` metadata (check datetimemod)
2. Explore available series in the release (always dump the full list first)
3. Select indicators based on economic relevance and data quality
4. Build time series charts and common factor (PCA) analysis
5. Polish scales, time windows, and styling
6. Archive session with dated script, outputs, and workflow notes

---

## Procedural Discoveries & Best Practices

### ✅ What Works Well

**Data discovery:**
- Have Claude Code dump the full list of available series early (don't guess)
- Filter by `datetimemod` to find what's actually in the latest release
- Check both NSA levels and SA variants; SA is usually better for PCA (avoids seasonal distortions)

**Indicator selection:**
- Jason picks from the full list based on economic theory (not Claude guessing)
- Aim for 4+ indicators for meaningful PCA (two-series PCA is pointless)
- Cross-check data quality: flag YTD cumulative reporting (FAI) as noisy; prefer monthly levels or SA

**Chart design:**
- Plotly for interactive exploration; matplotlib for final static output
- Always set y-axis limits based on the visible time window (5 years), not all historical data
- Use kaleido v0.2.1 (self-contained renderer, no Chrome needed)

**Code organization:**
- Date scripts and outputs by session (YYYYMMDD)
- One script per session in `sessions/YYYYMMDD/`
- Promote reusable functions to `sandbox/utils.py` as they prove their worth

### ❌ What Didn't Work

**Series selection by description matching:**
- Don't have Claude guess which series are "headline" — too easy to miss sub-components or assume wrong variants
- Early attempt: Claude suggested only IVA, FAI, Retail without seeing the full data. Jason had to push back.
- **Fix**: Always dump the full metadata list first, then filter collaboratively

**HTML chart output:**
- No one objected early on; wasted time converting to PNG later
- **Fix**: Decide output format upfront (PNG for static, interactive dashboards use different tools)

**Axis scaling from all available data:**
- Plotly auto-scales to the full series history, not the visible window
- Early charts had tiny bars because they were scaled to 2020–2026 instead of 2021–2026
- **Fix**: Filter to visible time window first, then set limits from that filtered data

**Package management surprises:**
- Tried to use Plotly's native image export; ended up needing kaleido v1 (requires Chrome)
- Pivoted to v0.2.1; fine, but decision should have been made upfront
- **Fix**: Decide on static vs. interactive output format before choosing libraries

---

## Next Session: Efficiency Checklist

To run this workflow faster on the next data release:

### Phase 1: Discovery (5–10 min)
- [ ] What's the release date? (e.g., Apr 15-16 for March data)
- [ ] Run Claude Code: dump all series with `datetimemod` in last 7 days
- [ ] Identify which themes are covered (GDP, activity, prices, employment, trade, financing)

### Phase 2: Design (10–15 min)
- [ ] In chat: identify 1–2 key stories (e.g., "tariff-driven export surge" or "activity slowdown")
- [ ] List candidate series for each story (4+ for PCA)
- [ ] Flag data quality issues (YTD base effects, NSA seasonality, etc.)
- [ ] Decide: how many charts? (e.g., 1 GDP context + 1 activity panel)

### Phase 3: Execution (10–20 min)
- [ ] Claude Code: load series, compute YoY/M/M, handle NaNs
- [ ] Build charts with 5-year window, tight y-axis limits
- [ ] Save as PNG to `output_YYYYMMDD/`
- [ ] Quick visual check (Jason confirms scales look right)

### Phase 4: Archive (5 min)
- [ ] Date the script, outputs, and workflow log
- [ ] Move to `sessions/YYYYMMDD/`
- [ ] Update main `README.md` with session link
- [ ] Commit and push

**Target**: 30–40 minutes from data release to three production-ready charts.

---

## Sessions

Each dated session lives in `sandbox/sessions/YYYYMMDD/`:
- `chart_builder_YYYYMMDD.py` — main script
- `output_YYYYMMDD/` — PNG charts
- `WORKFLOW_LOG_YYYYMMDD.md` — detailed notes, decisions, and lessons

### 2026-04-19: China Activity & GDP (Mar Release)

**Story**: Post-tariff frontloading in exports and manufacturing; broad-based activity slowdown offset by fiscal support.

**Charts**:
- GDP Q/Q SA + YoY (context)
- Activity YoY trends: IVA, Retail, Exports (SA), TSF
- Common factor (PCA) of four indicators

**Key decisions**:
- Dropped FAI from PCA (YTD base effect too noisy); added Exports (SA) instead
- Used SA exports to avoid +36% Lunar New Year spike
- 5-year time window with tight y-axis scaling

**Time**: ~60 min (first session, included debugging and workflow design)

**Lessons learned**: See `sessions/20260419/WORKFLOW_LOG_20260419.md`

---

## Shared Utilities

`sandbox/utils.py` accumulates reusable functions as they emerge from sessions:
- PCA factor computation
- YoY/M/M transforms
- Plotly chart templates with consistent styling

(Currently empty; will grow as workflows mature.)
