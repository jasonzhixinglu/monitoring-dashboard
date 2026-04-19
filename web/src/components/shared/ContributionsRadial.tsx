import Plot from "react-plotly.js";

interface Contribution {
  label: string;
  value: number;
}

interface Props {
  contributions: Contribution[];
  title?: string;
  emptyMessage?: string;
}

export function ContributionsRadial({
  contributions,
  title = "Factor Contributions (latest)",
  emptyMessage = "No contribution data",
}: Props) {
  if (contributions.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500 text-sm">
        {emptyMessage}
      </div>
    );
  }

  return (
    <Plot
      data={[{
        type: "barpolar",
        r: contributions.map((c) => Math.abs(c.value)),
        theta: contributions.map((c) => c.label),
        marker: {
          color: contributions.map((c) => (c.value >= 0 ? "#60a5fa" : "#f87171")),
        },
        name: "Contribution",
      }]}
      layout={{
        title: { text: title, font: { color: "#e5e7eb", size: 13 } },
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
  );
}
