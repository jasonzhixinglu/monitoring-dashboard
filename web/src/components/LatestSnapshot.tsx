import type { ThemeData } from "../types";

interface Props {
  data: ThemeData;
}

function fmtDate(isoDate: string): string {
  // "2026-03-01" → "2026-03"
  return isoDate.slice(0, 7);
}

export function LatestSnapshot({ data }: Props) {
  const allCols = Object.keys(data.inputs);

  const nameWidth = Math.max(...allCols.map((c) => c.length), "Common Factor (std dev)".length) + 1;
  const sep = "─".repeat(nameWidth + 10 + 9);

  const lines: string[] = [
    `Latest Data (as of ${data.vintage})`,
    sep,
    `${"Series".padEnd(nameWidth)} ${"Value".padStart(8)}  ${"As of".padStart(7)}`,
    sep,
  ];

  for (const col of allCols) {
    const { values, latest_date } = data.inputs[col];
    const v = [...values].reverse().find((x) => x !== null) ?? null;
    const valStr = v !== null ? v.toFixed(2).padStart(8) : "       —";
    lines.push(`${col.padEnd(nameWidth)} ${valStr}  ${fmtDate(latest_date).padStart(7)}`);
  }

  if (data.factor) {
    const { values, latest_date } = data.factor;
    const fv = [...values].reverse().find((x) => x !== null) ?? null;
    const valStr = fv !== null ? fv.toFixed(3).padStart(8) : "       —";
    lines.push(sep);
    lines.push(`${"Common Factor (std dev)".padEnd(nameWidth)} ${valStr}  ${fmtDate(latest_date).padStart(7)}`);
  }

  return (
    <div className="h-full bg-gray-950 rounded-lg p-3 overflow-auto">
      <pre className="text-xs text-green-300 font-mono leading-5 whitespace-pre">
        {lines.join("\n")}
      </pre>
    </div>
  );
}
