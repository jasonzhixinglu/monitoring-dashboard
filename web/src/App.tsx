import { useState } from "react";
import type { Country, Theme, YearWindow } from "./types";
import { Sidebar } from "./components/Sidebar";
import { ThemePage } from "./components/ThemePage";

export default function App() {
  const [country, setCountry] = useState<Country>("China");
  const [theme, setTheme] = useState<Theme>("activity");
  const [yearWindow, setYearWindow] = useState<YearWindow>(10);

  return (
    <div className="flex min-h-screen bg-gray-950 text-gray-100">
      <Sidebar
        country={country}
        theme={theme}
        yearWindow={yearWindow}
        onCountry={setCountry}
        onTheme={setTheme}
        onYearWindow={setYearWindow}
      />
      <main className="flex-1 p-6 overflow-auto">
        <ThemePage country={country} theme={theme} yearWindow={yearWindow} />
      </main>
    </div>
  );
}
