import type { Country, Theme, YearWindow, Mode, NowcastCountry, NowcastYearWindow } from "../types";

const YEAR_OPTIONS: YearWindow[] = [2, 3, 5, 10, 15, 20];
const NOWCAST_YEAR_OPTIONS: NowcastYearWindow[] = [3, 5, 10, 20];

interface Props {
  mode: Mode;
  country: Country;
  theme: Theme;
  yearWindow: YearWindow;
  nowcastCountry: NowcastCountry;
  nowcastYearWindow: NowcastYearWindow;
  onMode: (m: Mode) => void;
  onCountry: (c: Country) => void;
  onTheme: (t: Theme) => void;
  onYearWindow: (y: YearWindow) => void;
  onNowcastCountry: (c: NowcastCountry) => void;
  onNowcastYearWindow: (y: NowcastYearWindow) => void;
}

export function Sidebar({ mode, country, theme, yearWindow, nowcastCountry, nowcastYearWindow, onMode, onCountry, onTheme, onYearWindow, onNowcastCountry, onNowcastYearWindow }: Props) {
  return (
    <aside className="w-full md:w-52 shrink-0 bg-gray-900 text-gray-100 flex flex-row flex-wrap items-end md:flex-col gap-3 md:gap-6 px-3 py-2 md:p-4 md:min-h-screen">
      <div className="hidden md:block text-lg font-semibold tracking-wide border-b border-gray-700 pb-2 w-full">
        Controls
      </div>

      {/* Mode selector */}
      <div className="flex flex-col gap-1 w-full">
        <label className="text-xs text-gray-400 uppercase tracking-wider">Mode</label>
        <div className="flex rounded overflow-hidden border border-gray-700 text-sm">
          <button
            className={`flex-1 py-1.5 px-2 ${mode === "monitoring" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
            onClick={() => onMode("monitoring")}
          >
            Monitor
          </button>
          <button
            className={`flex-1 py-1.5 px-2 ${mode === "nowcasting" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
            onClick={() => onMode("nowcasting")}
          >
            Nowcast
          </button>
        </div>
      </div>

      {mode === "monitoring" ? (
        <>
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

          <div className="hidden md:flex flex-col gap-1">
            <label className="text-xs text-gray-400 uppercase tracking-wider">Outlier removal</label>
            <div className="flex items-center gap-2 opacity-50 cursor-not-allowed select-none">
              <div className="w-8 h-4 bg-blue-500 rounded-full relative">
                <div className="absolute right-0.5 top-0.5 w-3 h-3 bg-white rounded-full" />
              </div>
              <span className="text-xs text-gray-300">Enabled (pre-computed)</span>
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-400 uppercase tracking-wider">Country</label>
            <select
              className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={nowcastCountry}
              onChange={(e) => onNowcastCountry(e.target.value as NowcastCountry)}
            >
              <option value="US">United States</option>
              <option value="Japan">Japan</option>
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-400 uppercase tracking-wider">Year window</label>
            <select
              className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={nowcastYearWindow}
              onChange={(e) => onNowcastYearWindow(Number(e.target.value) as NowcastYearWindow)}
            >
              {NOWCAST_YEAR_OPTIONS.map((y) => (
                <option key={y} value={y}>{y} years</option>
              ))}
            </select>
          </div>
        </>
      )}
    </aside>
  );
}
