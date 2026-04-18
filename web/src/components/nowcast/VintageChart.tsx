import Plot from "react-plotly.js";
import type { NowcastData } from "../../types";

interface Props {
  data: NowcastData;
}

export function VintageChart({ data }: Props) {
  const { pseudo_vintages, nowcast_value, nowcast_quarter } = data;

  const firstDate = pseudo_vintages.dates[0] ?? "";
  const lastDate = pseudo_vintages.dates[pseudo_vintages.dates.length - 1] ?? "";

  return (
    <Plot
      data={[
        {
          x: pseudo_vintages.dates,
          y: pseudo_vintages.values,
          type: "scatter",
          mode: "lines+markers",
          name: "Nowcast",
          line: { color: "#60a5fa", width: 2 },
          marker: { size: 5 },
          connectgaps: false,
        },
        {
          x: [firstDate, lastDate],
          y: [nowcast_value, nowcast_value],
          type: "scatter",
          mode: "lines",
          name: `Final (${nowcast_quarter})`,
          line: { color: "#fbbf24", dash: "dash", width: 1.5 },
        },
      ]}
      layout={{
        title: { text: "Nowcast Evolution (Pseudo-Vintages)", font: { color: "#e5e7eb", size: 13 } },
        paper_bgcolor: "#111827",
        plot_bgcolor: "#111827",
        font: { color: "#9ca3af" },
        margin: { t: 35, r: 15, b: 40, l: 55 },
        xaxis: { gridcolor: "#374151", tickfont: { size: 10 } },
        yaxis: { gridcolor: "#374151", tickfont: { size: 10 }, title: { text: "% QOQAR", font: { size: 10 } } },
        legend: { font: { size: 10 } },
        height: 220,
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%" }}
    />
  );
}
