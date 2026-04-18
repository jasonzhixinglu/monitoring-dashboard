import { useState } from "react";
import type { Country, Theme, YearWindow, Mode, NowcastCountry, NowcastYearWindow } from "./types";
import { Sidebar } from "./components/Sidebar";
import { ThemePage } from "./components/ThemePage";
import { NowcastPage } from "./components/nowcast/NowcastPage";

export default function App() {
  const [mode, setMode] = useState<Mode>("monitoring");
  const [country, setCountry] = useState<Country>("China");
  const [theme, setTheme] = useState<Theme>("activity");
  const [yearWindow, setYearWindow] = useState<YearWindow>(10);
  const [nowcastCountry, setNowcastCountry] = useState<NowcastCountry>("US");
  const [nowcastYearWindow, setNowcastYearWindow] = useState<NowcastYearWindow>(5);

  return (
    <div className="flex flex-col md:flex-row min-h-screen bg-gray-950 text-gray-100">
      <Sidebar
        mode={mode}
        country={country}
        theme={theme}
        yearWindow={yearWindow}
        nowcastCountry={nowcastCountry}
        nowcastYearWindow={nowcastYearWindow}
        onMode={setMode}
        onCountry={setCountry}
        onTheme={setTheme}
        onYearWindow={setYearWindow}
        onNowcastCountry={setNowcastCountry}
        onNowcastYearWindow={setNowcastYearWindow}
      />
      <main className="flex-1 p-6 overflow-auto">
        {mode === "monitoring" ? (
          <ThemePage country={country} theme={theme} yearWindow={yearWindow} />
        ) : (
          <NowcastPage country={nowcastCountry} yearWindow={nowcastYearWindow} />
        )}
      </main>
    </div>
  );
}
