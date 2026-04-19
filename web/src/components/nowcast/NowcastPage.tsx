import { useMemo } from "react";
import type { NowcastCountry, NowcastData, NowcastYearWindow } from "../../types";
import { useNowcastData } from "../../hooks/useNowcastData";
import { useIsMobile } from "../../hooks/useIsMobile";
import { GDPChart } from "./GDPChart";
import { VintageChart } from "./VintageChart";
import { SnapshotBox } from "../shared/SnapshotBox";
import { SurpriseHeatmap } from "../shared/SurpriseHeatmap";
import { ContributionsRadial } from "../shared/ContributionsRadial";
import { DataTable } from "../shared/DataTable";
import { ModelDiagnostics } from "../shared/ModelDiagnostics";
import type { DiagEntry } from "../shared/ModelDiagnostics";

interface Props {
  country: NowcastCountry;
  yearWindow: NowcastYearWindow;
}

function buildNowcastSnapshot(data: NowcastData): string[] {
  const { nowcast_value, nowcast_ci, vintage_date, nowcast_quarter, pseudo_vintages } = data;
  const sep = "─".repeat(34);

  const vintageRows: { date: string; value: number }[] = [];
  for (let i = pseudo_vintages.dates.length - 1; i >= 0 && vintageRows.length < 6; i--) {
    const v = pseudo_vintages.values[i];
    if (v !== null && v !== undefined) {
      vintageRows.push({ date: pseudo_vintages.dates[i], value: v });
    }
  }

  const evolutionLines = [
    "",
    "Recent Evolution",
    sep,
    ...vintageRows.map((row, i) => {
      const revision = i === 0 ? "—" : (() => {
        const diff = row.value - vintageRows[i - 1].value;
        return (diff >= 0 ? "+" : "") + diff.toFixed(2);
      })();
      return `${row.date.padEnd(18)} ${(row.value.toFixed(2) + "%").padStart(7)}   ${revision.padStart(6)}`;
    }),
  ];

  return [
    "GDP Nowcast",
    sep,
    `${nowcast_quarter.padEnd(18)} ${nowcast_value.toFixed(2)}% QOQAR`,
    `${"95% CI".padEnd(18)} [${nowcast_ci[0].toFixed(2)}, ${nowcast_ci[1].toFixed(2)}]`,
    `${"As of".padEnd(18)} ${vintage_date}`,
    ...evolutionLines,
  ];
}

export function NowcastPage({ country, yearWindow }: Props) {
  const { data, loading, error } = useNowcastData(country);
  const isMobile = useIsMobile();

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

    const contributions = Object.keys(data.contributions)
      .filter((k) => data.contributions[k] != null && k !== "GDP Growth")
      .map((k) => ({ label: k, value: data.contributions[k] }));

    const inputCols = Object.keys(data.input_data);
    const allInputDates = inputCols.length > 0
      ? Array.from(new Set(inputCols.flatMap((c) => data.input_data[c].dates))).sort()
      : [];
    const last12InputDates = allInputDates.slice(-12);

    const transforms = data.transforms ?? {};
    const displayCols = inputCols.map((col) => {
      const t = transforms[col];
      return t ? `${col} [${t}]` : col;
    });

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

    const diagEntries: DiagEntry[] = Object.keys(data.loadings).map((col) => ({
      label: col,
      r2: data.r_squared[col] ?? 0,
      loadings: data.loadings[col] ?? [],
    }));

    return { surpCols, last24SurpDates, heatZ, contributions, tableText, csvContent, diagEntries };
  }, [data]);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-gray-400">Loading {country} nowcast…</div>;
  }
  if (error || !data || !derived) {
    return <div className="flex items-center justify-center h-64 text-red-400">Error: {error ?? "No data"}</div>;
  }

  const { surpCols, last24SurpDates, heatZ, contributions, tableText, csvContent, diagEntries } = derived;
  const snapshotLines = buildNowcastSnapshot(data);

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
          <SnapshotBox
            lines={snapshotLines}
            preClassName="text-xs text-green-300 font-mono leading-6 whitespace-pre"
          />
        </div>
      </div>

      {/* Bottom row: heatmap + radial */}
      <div className="flex flex-col md:grid md:grid-cols-2 gap-4">
        {surpCols.length > 0 && (
          <SurpriseHeatmap
            cols={surpCols}
            dates={last24SurpDates}
            z={heatZ}
            isMobile={isMobile}
          />
        )}
        {contributions.length > 0 && (
          <ContributionsRadial
            contributions={contributions}
            title={`Contributions (${data.nowcast_quarter})`}
          />
        )}
      </div>

      <DataTable
        tableText={tableText}
        csvContent={csvContent}
        filename={`${country.toLowerCase()}_nowcast_inputs.csv`}
        description="Input series — last 12 months (most recent first)"
      />

      <ModelDiagnostics
        entries={diagEntries}
        title="Model diagnostics (loadings, R²)"
      />
    </div>
  );
}
