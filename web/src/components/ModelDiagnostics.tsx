import { useState } from "react";
import type { ThemeData } from "../types";

interface Props {
  data: ThemeData;
}

export function ModelDiagnostics({ data }: Props) {
  const [open, setOpen] = useState(false);

  if (!data.diagnostics) return null;

  const { loadings, r_squared } = data.diagnostics;
  const cols = Object.keys(loadings);

  return (
    <div className="border border-gray-700 rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-2 bg-gray-800 hover:bg-gray-750 text-sm font-medium text-gray-200"
        onClick={() => setOpen((o) => !o)}
      >
        <span>Model diagnostics</span>
        <span className="text-gray-400">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="bg-gray-950 p-4 overflow-x-auto">
          <table className="text-xs font-mono text-gray-300 w-full">
            <thead>
              <tr className="border-b border-gray-700 text-gray-400">
                <th className="text-left pb-1 pr-4">Series</th>
                <th className="text-right pb-1 pr-4">R²</th>
                <th className="text-right pb-1">Loading</th>
              </tr>
            </thead>
            <tbody>
              {cols.map((col) => (
                <tr key={col} className="border-b border-gray-800">
                  <td className="py-0.5 pr-4">{col}</td>
                  <td className="text-right pr-4">{(r_squared[col] ?? 0).toFixed(3)}</td>
                  <td className="text-right">{(loadings[col] ?? 0).toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
