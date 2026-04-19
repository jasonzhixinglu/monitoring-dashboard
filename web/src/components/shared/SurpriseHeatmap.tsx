import Plot from "react-plotly.js";

interface Props {
  cols: string[];
  dates: string[];
  z: (number | null)[][];
  title?: string;
  isMobile: boolean;
}

export function SurpriseHeatmap({
  cols,
  dates,
  z,
  title = "Surprises (last 24 months)",
  isMobile,
}: Props) {
  return (
    <Plot
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      data={[{ z, x: dates, y: cols, type: "heatmap", colorscale: "RdBu", zmid: 0, showscale: true,
        ...(isMobile ? { colorbar: { thickness: 10, len: 0.6 } } : {}),
      } as any]}
      layout={{
        title: { text: title, font: { color: "#e5e7eb", size: isMobile ? 12 : 13 } },
        paper_bgcolor: "#111827",
        plot_bgcolor: "#111827",
        font: { color: "#9ca3af" },
        margin: isMobile ? { t: 40, r: 30, b: 60, l: 150 } : { t: 35, r: 15, b: 60, l: 220 },
        xaxis: { tickfont: { size: isMobile ? 8 : 9 }, tickangle: -45 },
        yaxis: { tickfont: { size: isMobile ? 8 : 9 }, autorange: "reversed" },
        height: 280,
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%" }}
    />
  );
}
