import { useMemo } from "react";
import type { Country, Theme, YearWindow, ThemeData } from "../types";
import { useThemeData } from "../hooks/useThemeData";
import { ChartGrid } from "./ChartGrid";
import { DataTable } from "./shared/DataTable";
import { ModelDiagnostics } from "./shared/ModelDiagnostics";
import type { DiagEntry } from "./shared/ModelDiagnostics";

interface Props {
  country: Country;
  theme: Theme;
  yearWindow: YearWindow;
}

function buildCsv(data: ThemeData): string {
  const cols = Object.keys(data.inputs);
  const header = ["date", ...(data.factor ? ["factor"] : []), ...cols].join(",");
  const rows = data.dates.map((d, i) => {
    const parts: (string | number | null)[] = [d];
    if (data.factor) parts.push(data.factor.values[i]);
    cols.forEach((col) => parts.push(data.inputs[col].values[i]));
    return parts.join(",");
  });
  return [header, ...rows].join("\n");
}

function formatTable(data: ThemeData, indices: number[]): string {
  const cols = Object.keys(data.inputs);
  const hasFactor = !!data.factor;

  const dateW = 7;
  const factorW = hasFactor ? 8 : 0;
  const colWidths = cols.map((col) => Math.max(col.length, 7));

  function pad(s: string | null | undefined, w: number, right = true): string {
    const str = s ?? "—";
    return right ? str.padStart(w) : str.padEnd(w);
  }

  function fmtNum(v: number | null, decimals: number): string {
    return v !== null ? v.toFixed(decimals) : "—";
  }

  const sepParts = [
    "─".repeat(dateW),
    ...(hasFactor ? ["─".repeat(factorW)] : []),
    ...colWidths.map((w) => "─".repeat(w)),
  ];
  const sep = sepParts.join("─┼─");

  const hdrParts = [
    pad("Date", dateW, false),
    ...(hasFactor ? [pad("Factor", factorW)] : []),
    ...cols.map((col, j) => pad(col, colWidths[j])),
  ];
  const header = hdrParts.join(" │ ");

  const rows = [...indices].reverse().map((i) => {
    const parts = [
      pad(data.dates[i].slice(0, 7), dateW, false),
      ...(hasFactor ? [pad(fmtNum(data.factor!.values[i], 3), factorW)] : []),
      ...cols.map((col, j) => pad(fmtNum(data.inputs[col].values[i], 2), colWidths[j])),
    ];
    return parts.join(" │ ");
  });

  return [header, sep, ...rows].join("\n");
}

function displayTheme(theme: string): string {
  if (theme === "pmis") return "PMIs";
  return theme.charAt(0).toUpperCase() + theme.slice(1);
}

export function ThemePage({ country, theme, yearWindow }: Props) {
  const { data, loading, error } = useThemeData(country, theme);

  const filteredIndices = useMemo(() => {
    if (!data) return [];
    const cutoff = new Date();
    cutoff.setFullYear(cutoff.getFullYear() - yearWindow);
    return data.dates
      .map((d, i) => ({ d, i }))
      .filter(({ d }) => new Date(d) >= cutoff)
      .map(({ i }) => i);
  }, [data, yearWindow]);

  const tableText = useMemo(() => {
    if (!data) return null;
    return formatTable(data, filteredIndices.slice(-12));
  }, [data, filteredIndices]);

  const csvContent = useMemo(() => (data ? buildCsv(data) : ""), [data]);

  const diagEntries = useMemo((): DiagEntry[] => {
    if (!data?.diagnostics) return [];
    return Object.keys(data.diagnostics.loadings).map((col) => ({
      label: col,
      r2: data.diagnostics!.r_squared[col] ?? 0,
      loadings: [data.diagnostics!.loadings[col] ?? 0],
    }));
  }, [data]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading {country} {theme}…
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-red-400">
        Error: {error ?? "Unknown error"}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold text-gray-100">
        {country} — {displayTheme(theme)}
      </h1>

      <ChartGrid data={data} filteredIndices={filteredIndices} />

      {tableText && (
        <DataTable
          tableText={tableText}
          csvContent={csvContent}
          filename={`${country.toLowerCase()}_${theme}_factor_inputs.csv`}
          description="Factor + transformed inputs — last 12 months (most recent first)"
        />
      )}

      <ModelDiagnostics entries={diagEntries} />
    </div>
  );
}
