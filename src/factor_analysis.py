import warnings
import numpy as np
import pandas as pd


def remove_outliers(dta: pd.DataFrame) -> pd.DataFrame:
    """Replace values > mean + 10*IQR with NaN (Fulton approach)."""
    mean = dta.mean()
    iqr = dta.quantile([0.25, 0.75]).diff().T.iloc[:, 1]
    mask = np.abs(dta) > mean + 10 * iqr
    treated = dta.copy()
    treated[mask] = np.nan
    return treated


def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    mu, sigma = df.mean(), df.std()
    sigma[sigma < 1e-12] = np.nan
    return (df - mu) / sigma


def _ols(y: np.ndarray, x: np.ndarray):
    """OLS of y on [1, x]. Returns (beta, residuals, r2)."""
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    ss_res = float(np.dot(resid, resid))
    ss_tot = float(np.dot(y - y.mean(), y - y.mean()))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0
    return beta, resid, r2


def _ar1_surprises(series: pd.Series) -> pd.Series:
    """One-step-ahead forecast errors from an AR(1) on the series."""
    clean = series.dropna()
    surprises = pd.Series(np.nan, index=series.index, dtype=float)
    if len(clean) < 4:
        return surprises
    y = clean.values
    _, resid, _ = _ols(y[1:], y[:-1])
    surprises.loc[clean.index[1:]] = resid
    return surprises


def extract_factor(
    df: pd.DataFrame,
    remove_outliers_flag: bool = True,
    pca_cols: list | None = None,
) -> dict:
    """Extract first principal component factor from a theme DataFrame.

    df: 'date' column + one column per indicator (post-transform values).
    pca_cols: if provided, only these columns enter PCA; all columns still get
              residuals and R² computed against the estimated factor.

    Missing-data contract
    ─────────────────────
    • No imputation or forward-fill is performed at any stage.
    • PCA uses listwise deletion: only rows where every pca_col is non-null
      (after standardisation and optional outlier removal) are used to fit the
      eigenvectors.  The factor is NaN for all other rows.
    • Consequence: the factor's latest non-null date equals the most recent date
      on which every PCA-eligible indicator has a real observation.  If one series
      lags by a month the factor will also lag by a month.
    • Residuals and R² are computed only where both the indicator and the factor
      are non-null (inner join on date).  No extrapolation is performed.
    • Surprises (AR(1) residuals of OLS residuals) follow the same rule —
      computed only on real data.

    Returns dict with keys:
        factor      — date-indexed pd.Series (mean-0, variance-1); NaN where any
                      PCA input was missing
        loadings    — {indicator: loading}  (PCA-eligible cols only)
        r_squared   — {indicator: R²}  (all indicator cols)
        residuals   — pd.DataFrame (date × indicators); NaN where data missing
        surprises   — pd.DataFrame (date × indicators); NaN where data missing

    Raises ValueError if PCA cannot be computed.
    """
    all_indicator_cols = [c for c in df.columns if c != "date"]
    pca_cols = pca_cols if pca_cols is not None else all_indicator_cols
    panel = df.set_index("date")[all_indicator_cols].copy()

    # Standardize full panel (no imputation — NaN rows stay NaN)
    std_panel = _standardize(panel)
    if remove_outliers_flag:
        std_panel = remove_outliers(std_panel)

    # Restrict to PCA-eligible columns with enough data
    pca_eligible = [
        c for c in pca_cols
        if c in std_panel.columns and std_panel[c].notna().sum() >= 12
    ]
    if len(pca_eligible) < 2:
        raise ValueError("Fewer than 2 PCA-eligible indicators with sufficient data.")

    pca_panel = std_panel[pca_eligible]

    # Listwise deletion: drop any row where any PCA column is NaN
    clean = pca_panel.dropna()
    min_rows = max(10, 2 * len(pca_eligible))
    if len(clean) < min_rows:
        raise ValueError(
            f"Only {len(clean)} complete rows after NaN removal (need ≥{min_rows})."
        )

    X = clean.values  # (T × N)

    # PCA via eigendecomposition of correlation matrix
    corr = np.corrcoef(X.T)
    eigenvalues, eigenvectors = np.linalg.eigh(corr)
    pc1 = eigenvectors[:, -1]  # eigh returns ascending; last = largest eigenvalue

    # Sign convention: positive = expansion / high readings
    if pc1.mean() < 0:
        pc1 = -pc1

    # Project only the clean rows; factor is NaN everywhere else (no fill)
    factor_clean = X @ pc1
    factor_clean = (factor_clean - factor_clean.mean()) / factor_clean.std()
    factor = pd.Series(np.nan, index=panel.index, dtype=float)
    factor.loc[clean.index] = factor_clean

    loadings = {col: float(pc1[i]) for i, col in enumerate(pca_eligible)}

    # Per-indicator residuals and surprises for ALL indicator columns
    # Inner join with factor — no extrapolation into NaN regions
    r_squared, residuals_dict, surprises_dict = {}, {}, {}
    for col in all_indicator_cols:
        both = pd.DataFrame({"y": std_panel[col], "f": factor}).dropna()
        if len(both) < 4:
            warnings.warn(f"Skipping residuals for '{col}': insufficient overlap with factor.")
            continue
        _, resid, r2 = _ols(both["y"].values, both["f"].values)
        r_squared[col] = round(r2, 3)
        resid_series = pd.Series(np.nan, index=std_panel.index, dtype=float)
        resid_series.loc[both.index] = resid
        residuals_dict[col] = resid_series
        surprises_dict[col] = _ar1_surprises(resid_series)

    return {
        "factor": factor,
        "loadings": loadings,
        "r_squared": r_squared,
        "residuals": pd.DataFrame(residuals_dict),
        "surprises": pd.DataFrame(surprises_dict),
    }
