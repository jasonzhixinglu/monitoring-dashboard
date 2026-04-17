export interface SeriesData {
  values: (number | null)[];
  latest_date: string;
}

export interface FactorData {
  values: (number | null)[];
  latest_date: string;
}

export interface ThemeData {
  country: string;
  theme: string;
  vintage: string;
  dates: string[];
  factor?: FactorData;
  inputs: Record<string, SeriesData>;
  diagnostics?: {
    loadings: Record<string, number>;
    r_squared: Record<string, number>;
  };
}

export type Country = "China" | "Japan";
export type Theme = "activity" | "inflation" | "pmis";
export type YearWindow = 2 | 3 | 5 | 10 | 15 | 20;
