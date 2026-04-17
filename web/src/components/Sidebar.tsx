import type { Country, Theme, YearWindow } from "../types";

const YEAR_OPTIONS: YearWindow[] = [2, 3, 5, 10, 15, 20];

interface Props {
  country: Country;
  theme: Theme;
  yearWindow: YearWindow;
  onCountry: (c: Country) => void;
  onTheme: (t: Theme) => void;
  onYearWindow: (y: YearWindow) => void;
}

export function Sidebar({ country, theme, yearWindow, onCountry, onTheme, onYearWindow }: Props) {
  return (
    <aside className="w-52 shrink-0 bg-gray-900 text-gray-100 flex flex-col gap-6 p-4 min-h-screen">
      <div className="text-lg font-semibold tracking-wide border-b border-gray-700 pb-2">
        Controls
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400 uppercase tracking-wider">Country</label>
        <select
          className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          value={country}
          onChange={(e) => onCountry(e.target.value as Country)}
        >
          <option value="China">China</option>
          <option value="Japan">Japan</option>
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400 uppercase tracking-wider">Theme</label>
        <select
          className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          value={theme}
          onChange={(e) => onTheme(e.target.value as Theme)}
        >
          <option value="activity">Activity</option>
          <option value="inflation">Inflation</option>
          <option value="pmis">PMIs</option>
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400 uppercase tracking-wider">Year window</label>
        <select
          className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          value={yearWindow}
          onChange={(e) => onYearWindow(Number(e.target.value) as YearWindow)}
        >
          {YEAR_OPTIONS.map((y) => (
            <option key={y} value={y}>{y} years</option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400 uppercase tracking-wider">Outlier removal</label>
        <div className="flex items-center gap-2 opacity-50 cursor-not-allowed select-none">
          <div className="w-8 h-4 bg-blue-500 rounded-full relative">
            <div className="absolute right-0.5 top-0.5 w-3 h-3 bg-white rounded-full" />
          </div>
          <span className="text-xs text-gray-300">Enabled (pre-computed)</span>
        </div>
      </div>
    </aside>
  );
}
