import { useState, useEffect } from "react";
import type { ThemeData, Country, Theme } from "../types";

interface UseThemeDataResult {
  data: ThemeData | null;
  loading: boolean;
  error: string | null;
}

const cache: Record<string, ThemeData> = {};

export function useThemeData(country: Country, theme: Theme): UseThemeDataResult {
  const key = `${country.toLowerCase()}_${theme}`;
  const [data, setData] = useState<ThemeData | null>(cache[key] ?? null);
  const [loading, setLoading] = useState<boolean>(!cache[key]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (cache[key]) {
      setData(cache[key]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);

    import(`../data/${key}.json`)
      .then((mod) => {
        const loaded = mod.default as ThemeData;
        cache[key] = loaded;
        setData(loaded);
        setLoading(false);
      })
      .catch((err: unknown) => {
        setError(String(err));
        setLoading(false);
      });
  }, [key]);

  return { data, loading, error };
}
