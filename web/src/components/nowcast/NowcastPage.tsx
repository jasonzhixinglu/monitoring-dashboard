import { useEffect, useMemo, useState } from "react";
import Plot from "react-plotly.js";
import type { NowcastCountry, NowcastData, NowcastYearWindow } from "../../types";
import { useNowcastData } from "../../hooks/useNowcastData";
import { GDPChart } from "./GDPChart";
import { VintageChart } from "./VintageChart";

interface Props {
  country: NowcastCountry;
  yearWindow: NowcastYearWindow;
}

function useIsMobile(breakpoint = 768): boolean {
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < breakpoint);
  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth < breakpoint);
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, [breakpoint]);
  return isMobile;
}

function NowcastSnapshot({ data }: { data: NowcastData }) {
  const { nowcast_value, nowcast_ci, vintage_date, nowcast_quarter } = data;
  const sep = "─".repeat(34);
  const lines = [
    "GDP Nowcast",
    sep,
    `${nowcast_quarter.padEnd(18)} ${nowcast_value.toFixed(2)}% QOQAR`,
    `${"95% CI".padEnd(18)} [${nowcast_ci[0].toFixed(2)}, ${nowcast_ci[1].toFixed(2)}]`,
    `${"As of".padEnd(18)} ${vintage_date}`,
  ];
  return (
    <div className="bg-gray-950 rounded-lg p-4 h-full">
      <pre className="text-xs text-green-300 font-mono leading-6 whitespace-pre">{lines.join("\n")}</pre>
    </div>
  );
}

export function NowcastPage({ country, yearWindow }: Props) {
  const { data, loading, error } = useNowcastData(country);
  const [diagOpen, setDiagOpen] = useState(false);
  const isMobile = useIsMobile();

  // All hooks must be called unconditionally before any early returns
  const derived = useMemo(() => {
    if (!data) return null;

    const surpCols = Object.keys(data.surprises);
    const allSurpDates = Array.from(
      new Set(surpCols.flatMap((c) => data.surprises[c].dates))
    ).sort();
    const last24SurpDates = allSurpDates.slice(-24);
    const heatZ = surpCols.map((col) => {
      const dateMap = new Map(
        data.surprises[col].dates.map((d, i) => [d, data.surprises[col].values[i]])
      );
      return last24SurpDates.map((d) => dateMap.get(d) ?? null);
    });

    const contribKeys = Object.keys(data.contributions).filter(
      (k) => data.contributions[k] != null && k !== "GDP Growth"
    );

    const inputCols = Object.keys(data.input_data);
    const allInputDates = inputCols.length > 0
      ? Array.from(new Set(inputCols.flatMap((c) => data.input_data[c].dates))).sort()
      : [];
    const last12InputDates = allInputDates.slice(-12);

    // Build display column names: "Industrial Production [3m3mar]"
    const transforms = data.transforms ?? {};
    const displayCols = inputCols.map((col) => {
      const t = transforms[col];
      return t ? `${col} [${t}]` : col;
    });

    // Monospace table matching monitoring dashboard format
    const dateW = 7;
    const colWidths = displayCols.map((c) => Math.max(c.length, 7));
    function pad(s: string | null | undefined, w: number, right = true): string {
      const str = s ?? "—";
      return right ? str.padStart(w) : str.padEnd(w);
    }
    const sep = ["─".repeat(dateW), ...colWidths.map((w) => "─".repeat(w))].join("─┼─");
    const header = [pad("Date", dateW, false), ...displayCols.map((c, j) => pad(c, colWidths[j]))].join(" │ ");
    const tableRows = [...last12InputDates].reverse().map((d) => {
      const parts = [
        pad(d.slice(0, 7), dateW, false),
        ...inputCols.map((col, j) => {
          const s = data.input_data[col];
          const i = s.dates.indexOf(d);
          const v = i >= 0 ? s.values[i] : null;
          return pad(v !== null ? v.toFixed(2) : "—", colWidths[j]);
        }),
      ];
      return parts.join(" │ ");
    });
    const tableText = [header, sep, ...tableRows].join("\n");

    // CSV uses full date history
    const csvHeader = ["date", ...inputCols].join(",");
    const csvRows = allInputDates.map((d) => {
      const vals = inputCols.map((col) => {
        const s = data.input_data[col];
        const i = s.dates.indexOf(d);
        return i >= 0 ? (s.values[i] ?? "") : "";
      });
      return [d, ...vals].join(",");
    });
    const csvContent = [csvHeader, ...csvRows].join("\n");

    const loadingCols = Object.keys(data.loadings);
    const diagLines = loadingCols.length > 0 ? [
      `${"Series".padEnd(30)} ${"R²".padStart(6)}  ${"F1".padStart(8)}  ${"F2".padStart(8)}`,
      "─".repeat(58),
      ...loadingCols.map((col) => {
        const r2 = (data.r_squared[col] ?? 0).toFixed(3);
        const f1 = (data.loadings[col]?.[0] ?? 0).toFixed(3);
        const f2 = (data.loadings[col]?.[1] ?? 0).toFixed(3);
        return `${col.padEnd(30)} ${r2.padStart(6)}  ${f1.padStart(8)}  ${f2.padStart(8)}`;
      }),
    ].join("\n") : null;

    return { surpCols, last24SurpDates, heatZ, contribKeys, tableText, csvContent, diagLines };
  }, [data]);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading {country} nowcast…</div>;
  }
  if (error || !data || !derived) {
    return <div className="flex items-center justify-center h-64 text-red-400">Error: {error ?? "No data"}</div>;
  }

  const { surpCols, last24SurpDates, heatZ, contribKeys, tableText, csvContent, diagLines } = derived;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold text-gray-100">
        {country} — GDP Nowcast ({data.nowcast_quarter})
      </h1>

      {/* Top row: charts (left ~60%) + snapshot (right ~40%) */}
      <div className="flex flex-col md:grid md:grid-cols-5 gap-4">
        <div className="md:col-span-3 flex flex-col gap-3">
          <GDPChart data={data} yearWindow={yearWindow} />
          <VintageChart data={data} />
        </div>
        <div className="md:col-span-2">
          <NowcastSnapshot data={data} />
        </div>
      </div>

      {/* Bottom row: heatmap + radial */}
      <div className="flex flex-col md:grid md:grid-cols-2 gap-4">
        {surpCols.length > 0 && (
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          <Plot
            data={[{
              z: heatZ, x: last24SurpDates, y: surpCols, type: "heatmap",
              colorscale: "RdBu", zmid: 0, showscale: true,
              ...(isMobile ? { colorbar: { thickness: 10, len: 0.6 } } : {}),
            } as any]}
            layout={{
              title: { text: "Surprises (last 24 months)", font: { color: "#e5e7eb", size: isMobile ? 12 : 13 } },
              paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#9ca3af" },
              margin: isMobile ? { t: 40, r: 30, b: 60, l: 150 } : { t: 35, r: 15, b: 60, l: 220 },
              xaxis: { tickfont: { size: isMobile ? 8 : 9 }, tickangle: -45 },
              yaxis: { tickfont: { size: isMobile ? 8 : 9 }, autorange: "reversed" },
              height: 280,
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%" }}
          />
        )}
        {contribKeys.length > 0 && (
          <Plot
            data={[{
              type: "barpolar",
              r: contribKeys.map((k) => Math.abs(data.contributions[k] ?? 0)),
              theta: contribKeys,
              marker: { color: contribKeys.map((k) => (data.contributions[k] ?? 0) >= 0 ? "#60a5fa" : "#f87171") },
            }]}
            layout={{
              title: { text: `Contributions (${data.nowcast_quarter})`, font: { color: "#e5e7eb", size: 13 } },
              paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#9ca3af", size: 9 },
              polar: { bgcolor: "#1f2937", angularaxis: { tickfont: { size: 9 }, gridcolor: "#374151" }, radialaxis: { gridcolor: "#374151" } },
              margin: { t: 40, r: 20, b: 20, l: 20 }, height: 280, showlegend: false,
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%" }}
          />
        )}
      </div>

      {/* Input data table — monospace, matches monitoring dashboard format */}
      <div className="bg-gray-900 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">
            Input series — last 12 months (most recent first)
          </span>
          <button
            onClick={() => {
              const blob = new Blob([csvContent], { type: "text/csv" });
              const a = document.createElement("a");
              a.href = URL.createObjectURL(blob);
              a.download = `${country.toLowerCase()}_nowcast_inputs.csv`;
              a.click();
            }}
            className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded"
          >
            Download CSV (full history)
          </button>
        </div>
        <pre className="text-xs font-mono text-gray-300 overflow-x-auto whitespace-pre leading-5">
          {tableText}
        </pre>
      </div>

      {/* Model diagnostics */}
      {diagLines && (
        <div className="border border-gray-700 rounded-lg overflow-hidden">
          <button
            className="w-full flex items-center justify-between px-4 py-2 bg-gray-800 text-sm font-medium text-gray-200"
            onClick={() => setDiagOpen((o) => !o)}
          >
            <span>Model diagnostics (loadings, R²)</span>
            <span className="text-gray-400">{diagOpen ? "▲" : "▼"}</span>
          </button>
          {diagOpen && (
            <div className="bg-gray-950 p-4 overflow-x-auto">
              <pre className="text-xs font-mono text-gray-300 leading-5">{diagLines}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
