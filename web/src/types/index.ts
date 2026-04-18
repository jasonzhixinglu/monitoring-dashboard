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
export type Mode = "monitoring" | "nowcasting";
export type NowcastCountry = "US" | "Japan";
export type NowcastYearWindow = 3 | 5 | 10 | 20;

export interface NowcastSeriesData {
  dates: string[];
  values: (number | null)[];
}

export interface NowcastData {
  country: string;
  nowcast_quarter: string;
  vintage_date: string;
  nowcast_value: number;
  nowcast_ci: [number, number];
  target_history: NowcastSeriesData;
  pseudo_vintages: NowcastSeriesData;
  input_data: Record<string, NowcastSeriesData>;
  surprises: Record<string, NowcastSeriesData>;
  contributions: Record<string, number>;
  loadings: Record<string, number[]>;
  r_squared: Record<string, number>;
}
