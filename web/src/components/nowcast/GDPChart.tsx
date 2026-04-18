import Plot from "react-plotly.js";
import type { NowcastData } from "../../types";

interface Props {
  data: NowcastData;
  yearWindow: number;
}

// Parse "YYYY-MM-DD" → quarter label "2025-Q4" for hover text
function toQuarterLabel(dateStr: string): string {
  const d = new Date(dateStr);
  const q = Math.floor(d.getMonth() / 3) + 1;
  return `${d.getFullYear()}-Q${q}`;
}

export function GDPChart({ data, yearWindow }: Props) {
  const { target_history, nowcast_value, nowcast_ci, nowcast_quarter } = data;

  const cutoff = new Date();
  cutoff.setFullYear(cutoff.getFullYear() - yearWindow);

  const histDates: string[] = [];
  const histValues: (number | null)[] = [];
  const histLabels: string[] = [];
  for (let i = 0; i < target_history.dates.length; i++) {
    if (new Date(target_history.dates[i]) >= cutoff) {
      histDates.push(target_history.dates[i]);
      histValues.push(target_history.values[i]);
      histLabels.push(toQuarterLabel(target_history.dates[i]));
    }
  }

  // Q1 2026 bounds for the CI fill band
  const ciStart = "2026-01-01";
  const ciEnd = "2026-03-31";
  const ncMid = "2026-02-15";

  return (
    <Plot
      data={[
        // Historical GDP bars
        {
          x: histDates,
          y: histValues,
          customdata: histLabels,
          type: "bar",
          name: "GDP Growth",
          marker: { color: "#4b5563" },
          hovertemplate: "%{customdata}: %{y:.2f}%<extra></extra>",
        },
        // CI upper bound — invisible line (must come BEFORE lower so tonexty fills up to it)
        {
          x: [ciStart, ciEnd],
          y: [nowcast_ci[1], nowcast_ci[1]],
          type: "scatter",
          mode: "lines",
          line: { width: 0 },
          showlegend: false,
          name: "CI Upper",
          hoverinfo: "skip",
        },
        // CI lower bound — filled to previous trace (the upper bound)
        {
          x: [ciStart, ciEnd],
          y: [nowcast_ci[0], nowcast_ci[0]],
          type: "scatter",
          mode: "lines",
          fill: "tonexty",
          fillcolor: "rgba(99,110,250,0.25)",
          line: { width: 0 },
          showlegend: false,
          name: "CI Lower",
          hoverinfo: "skip",
        },
        // Nowcast point
        {
          x: [ncMid],
          y: [nowcast_value],
          type: "scatter",
          mode: "markers",
          name: nowcast_quarter,
          marker: { size: 11, color: "rgb(99,110,250)", symbol: "diamond" },
          hovertemplate: `${nowcast_quarter}: %{y:.2f}%<extra></extra>`,
        },
      ]}
      layout={{
        title: { text: `GDP Growth — ${nowcast_quarter} Nowcast`, font: { color: "#e5e7eb", size: 13 } },
        paper_bgcolor: "#111827",
        plot_bgcolor: "#111827",
        font: { color: "#9ca3af" },
        margin: { t: 35, r: 15, b: 45, l: 55 },
        xaxis: {
          gridcolor: "#374151",
          tickfont: { size: 9 },
          tickformat: "%Y",
          dtick: "M12",
          type: "date",
        },
        yaxis: {
          gridcolor: "#374151",
          tickfont: { size: 10 },
          title: { text: "% QOQAR", font: { size: 10 } },
          zeroline: true,
          zerolinecolor: "#6b7280",
          zerolinewidth: 1,
        },
        legend: { font: { size: 10 } },
        height: 280,
        bargap: 0.1,
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%" }}
    />
  );
}
