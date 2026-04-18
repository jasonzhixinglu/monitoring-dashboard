import { useState, useEffect } from "react";
import type { NowcastData, NowcastCountry } from "../types";

interface UseNowcastDataResult {
  data: NowcastData | null;
  loading: boolean;
  error: string | null;
}

const cache: Record<string, NowcastData> = {};

export function useNowcastData(country: NowcastCountry): UseNowcastDataResult {
  const key = `${country.toLowerCase()}_nowcast`;
  const [data, setData] = useState<NowcastData | null>(cache[key] ?? null);
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
        const loaded = mod.default as NowcastData;
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
