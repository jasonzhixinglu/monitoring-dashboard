import Plot from "react-plotly.js";
import type { NowcastData } from "../../types";

interface Props {
  data: NowcastData;
}

export function GDPChart({ data }: Props) {
  const { target_history, nowcast_value, nowcast_ci, nowcast_quarter } = data;

  const tenYearsAgo = new Date();
  tenYearsAgo.setFullYear(tenYearsAgo.getFullYear() - 10);

  const histDates: string[] = [];
  const histValues: (number | null)[] = [];
  for (let i = 0; i < target_history.dates.length; i++) {
    if (new Date(target_history.dates[i]) >= tenYearsAgo) {
      histDates.push(target_history.dates[i]);
      histValues.push(target_history.values[i]);
    }
  }

  // Midpoint of Q1 2026 as the nowcast x-position
  const ncDate = "2026-02-15";

  return (
    <Plot
      data={[
        {
          x: histDates,
          y: histValues,
          type: "bar",
          name: "GDP Growth",
          marker: { color: "#4b5563" },
        },
        {
          x: [ncDate],
          y: [nowcast_value],
          type: "scatter",
          mode: "markers",
          name: "Nowcast",
          marker: { color: "#fbbf24", size: 12, symbol: "diamond" },
          error_y: {
            type: "data",
            array: [nowcast_ci[1] - nowcast_value],
            arrayminus: [nowcast_value - nowcast_ci[0]],
            visible: true,
            color: "#fbbf24",
            thickness: 2,
            width: 6,
          },
        },
      ]}
      layout={{
        title: { text: `GDP Growth — ${nowcast_quarter} Nowcast`, font: { color: "#e5e7eb", size: 13 } },
        paper_bgcolor: "#111827",
        plot_bgcolor: "#111827",
        font: { color: "#9ca3af" },
        margin: { t: 35, r: 15, b: 40, l: 55 },
        xaxis: { gridcolor: "#374151", tickfont: { size: 10 } },
        yaxis: { gridcolor: "#374151", tickfont: { size: 10 }, title: { text: "% QOQAR", font: { size: 10 } } },
        legend: { font: { size: 10 } },
        height: 260,
        bargap: 0.1,
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%" }}
    />
  );
}
