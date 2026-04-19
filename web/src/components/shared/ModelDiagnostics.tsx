import { useState } from "react";

export interface DiagEntry {
  label: string;
  r2: number;
  loadings: number[];
}

interface Props {
  entries: DiagEntry[];
  title?: string;
}

export function ModelDiagnostics({ entries, title = "Model diagnostics" }: Props) {
  const [open, setOpen] = useState(false);

  if (entries.length === 0) return null;

  const twoFactor = entries.some((e) => e.loadings.length > 1);
  const sepLen = twoFactor ? 58 : 48;

  const diagText = [
    `${"Series".padEnd(30)} ${"R²".padStart(6)}  ${"F1".padStart(8)}${twoFactor ? `  ${"F2".padStart(8)}` : ""}`,
    "─".repeat(sepLen),
    ...entries.map((e) => {
      const r2 = (e.r2 ?? 0).toFixed(3);
      const f1 = (e.loadings[0] ?? 0).toFixed(3);
      const f2 = e.loadings[1] !== undefined ? e.loadings[1].toFixed(3) : null;
      return `${e.label.padEnd(30)} ${r2.padStart(6)}  ${f1.padStart(8)}${twoFactor && f2 !== null ? `  ${f2.padStart(8)}` : ""}`;
    }),
  ].join("\n");

  return (
    <div className="border border-gray-700 rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-2 bg-gray-800 hover:bg-gray-750 text-sm font-medium text-gray-200"
        onClick={() => setOpen((o) => !o)}
      >
        <span>{title}</span>
        <span className="text-gray-400">{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="bg-gray-950 p-4 overflow-x-auto">
          <pre className="text-xs font-mono text-gray-300 leading-5">{diagText}</pre>
        </div>
      )}
    </div>
  );
}
