import Plot from "react-plotly.js";
import type { ThemeData } from "../types";
import { LatestSnapshot } from "./LatestSnapshot";

interface Props {
  data: ThemeData;
  filteredIndices: number[];
}

const PALETTE = [
  "#60a5fa", "#34d399", "#f472b6", "#fb923c", "#a78bfa", "#facc15",
];

function nullableTrace(dates: string[], values: (number | null)[]) {
  return { x: dates, y: values };
}

export function ChartGrid({ data, filteredIndices }: Props) {
  const dates = filteredIndices.map((i) => data.dates[i]);
  const inputCols = Object.keys(data.inputs);

  // ── Factor chart ──────────────────────────────────────────────────────────
  const factorTrace = data.factor
    ? nullableTrace(dates, filteredIndices.map((i) => data.factor!.values[i]))
    : null;

  // ── Standardized inputs ───────────────────────────────────────────────────
  function zScore(col: string): (number | null)[] {
    const vals = filteredIndices.map((i) => data.inputs[col].values[i]);
    const nonNull = vals.filter((v): v is number => v !== null);
    if (nonNull.length === 0) return vals;
    const mean = nonNull.reduce((a, b) => a + b, 0) / nonNull.length;
    const std = Math.sqrt(nonNull.reduce((a, b) => a + (b - mean) ** 2, 0) / nonNull.length);
    if (std < 1e-12) return vals.map((v) => (v === null ? null : 0));
    return vals.map((v) => (v === null ? null : (v - mean) / std));
  }

  // ── Surprise heatmap ──────────────────────────────────────────────────────
  // Compute AR(1) residuals client-side from z-scored inputs
  function ar1Residuals(col: string): (number | null)[] {
    const zs = zScore(col);
    const result: (number | null)[] = new Array(zs.length).fill(null);
    const validIdx = zs.map((v, i) => (v !== null ? i : -1)).filter((i) => i >= 0);
    if (validIdx.length < 4) return result;
    const y = validIdx.map((i) => zs[i] as number);
    // OLS of y[1:] on y[:-1]
    const n = y.length - 1;
    let sx = 0, sy = 0, sxy = 0, sxx = 0;
    for (let i = 0; i < n; i++) {
      sx += y[i]; sy += y[i + 1]; sxy += y[i] * y[i + 1]; sxx += y[i] * y[i];
    }
    const beta1 = (n * sxy - sx * sy) / (n * sxx - sx * sx || 1);
    const beta0 = (sy - beta1 * sx) / n;
    for (let i = 0; i < n; i++) {
      result[validIdx[i + 1]] = y[i + 1] - (beta0 + beta1 * y[i]);
    }
    return result;
  }

  const last24Idx = filteredIndices.slice(-24);
  const last24Dates = last24Idx.map((i) => data.dates[i]);

  const heatZ = inputCols.map((col) => {
    const resids = ar1Residuals(col);
    return last24Idx.map((i) => {
      const local = filteredIndices.indexOf(i);
      return resids[local] ?? null;
    });
  });

  // ── Radial contributions (latest residuals × loadings) ────────────────────
  const contributions: { col: string; value: number }[] = [];
  if (data.diagnostics) {
    for (const col of inputCols) {
      const loading = data.diagnostics.loadings[col];
      if (loading === undefined) continue;
      const resids = ar1Residuals(col);
      const lastResid = [...resids].reverse().find((v) => v !== null) ?? null;
      if (lastResid !== null) contributions.push({ col, value: loading * lastResid });
    }
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Top-left: factor + indicators stacked */}
      <div className="flex flex-col gap-3">
        {factorTrace ? (
          <Plot
            data={[
              {
                ...factorTrace,
                type: "scatter",
                mode: "lines",
                name: "Factor",
                line: { color: "#60a5fa", width: 2 },
              },
              {
                x: [dates[0], dates[dates.length - 1]],
                y: [0, 0],
                type: "scatter",
                mode: "lines",
                line: { color: "#6b7280", dash: "dash", width: 1 },
                showlegend: false,
                hoverinfo: "skip",
              },
            ]}
            layout={{
              title: { text: "Common Factor", font: { color: "#e5e7eb", size: 13 } },
              paper_bgcolor: "#111827",
              plot_bgcolor: "#111827",
              font: { color: "#9ca3af" },
              margin: { t: 35, r: 15, b: 40, l: 45 },
              xaxis: { gridcolor: "#374151", tickfont: { size: 10 } },
              yaxis: { gridcolor: "#374151", tickfont: { size: 10 } },
              legend: { font: { size: 10 } },
              height: 220,
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%" }}
          />
        ) : null}

        <Plot
          data={inputCols.map((col, i) => ({
            x: dates,
            y: zScore(col),
            type: "scatter",
            mode: "lines",
            name: col,
            line: { color: PALETTE[i % PALETTE.length], width: 1.5 },
          }))}
          layout={{
            title: { text: "Standardized Indicators", font: { color: "#e5e7eb", size: 13 } },
            paper_bgcolor: "#111827",
            plot_bgcolor: "#111827",
            font: { color: "#9ca3af" },
            margin: { t: 35, r: 15, b: 40, l: 45 },
            xaxis: { gridcolor: "#374151", tickfont: { size: 10 } },
            yaxis: { gridcolor: "#374151", tickfont: { size: 10 } },
            legend: { font: { size: 9 }, orientation: "h", y: -0.25 },
            height: 260,
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: "100%" }}
        />
      </div>

      {/* Top-right: latest snapshot */}
      <div>
        <LatestSnapshot data={data} />
      </div>

      {/* Bottom-left: surprise heatmap */}
      <div>
        <Plot
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          data={[{ z: heatZ, x: last24Dates, y: inputCols, type: "heatmap", colorscale: "RdBu", zmid: 0, showscale: true } as any]}
          layout={{
            title: { text: "Surprises (last 24 months)", font: { color: "#e5e7eb", size: 13 } },
            paper_bgcolor: "#111827",
            plot_bgcolor: "#111827",
            font: { color: "#9ca3af" },
            margin: { t: 35, r: 15, b: 60, l: 220 },
            xaxis: { tickfont: { size: 9 }, tickangle: -45 },
            yaxis: { tickfont: { size: 9 }, autorange: "reversed" },
            height: 280,
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: "100%" }}
        />
      </div>

      {/* Bottom-right: radial contributions */}
      <div>
        {contributions.length > 0 ? (
          <Plot
            data={[
              {
                type: "barpolar",
                r: contributions.map((c) => Math.abs(c.value)),
                theta: contributions.map((c) => c.col),
                marker: {
                  color: contributions.map((c) =>
                    c.value >= 0 ? "#60a5fa" : "#f87171"
                  ),
                },
                name: "Contribution",
              },
            ]}
            layout={{
              title: { text: "Factor Contributions (latest)", font: { color: "#e5e7eb", size: 13 } },
              paper_bgcolor: "#111827",
              plot_bgcolor: "#111827",
              font: { color: "#9ca3af", size: 9 },
              polar: {
                bgcolor: "#1f2937",
                angularaxis: { tickfont: { size: 9 }, gridcolor: "#374151" },
                radialaxis: { gridcolor: "#374151" },
              },
              margin: { t: 40, r: 20, b: 20, l: 20 },
              height: 280,
              showlegend: false,
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%" }}
          />
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500 text-sm">
            No contribution data (PMIs have no factor)
          </div>
        )}
      </div>
    </div>
  );
}
