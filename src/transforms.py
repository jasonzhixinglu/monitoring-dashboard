import pandas as pd


def compute_3m3mar(s: pd.Series) -> pd.Series:
    """3-month over 3-month annualized rate: ((s / s.shift(3)) ** 4 - 1) * 100."""
    return ((s / s.shift(3)) ** 4 - 1) * 100


def compute_qoqar(s: pd.Series) -> pd.Series:
    """Quarter-over-quarter annualized rate from level: ((s / s.shift(1)) ** 4 - 1) * 100."""
    return ((s / s.shift(1)) ** 4 - 1) * 100


def apply_transform(s: pd.Series, transform: str) -> pd.Series:
    """Apply a named transform to a date-indexed Series.

    Supported transforms:
        level   — return as-is
        yoy     — year-over-year % change: (v / v.shift(12) - 1) * 100
        mom     — month-over-month % change: (v / v.shift(1) - 1) * 100
        3m3mar  — 3-month over 3-month annualized rate
        qoqar   — quarter-over-quarter annualized rate (from level)
    """
    if transform == "level":
        return s
    if transform == "yoy":
        return (s / s.shift(12) - 1) * 100
    if transform == "mom":
        return (s / s.shift(1) - 1) * 100
    if transform == "3m3mar":
        return compute_3m3mar(s)
    if transform == "qoqar":
        return compute_qoqar(s)
    raise ValueError(f"Unknown transform '{transform}'. Choose from: level, yoy, mom, 3m3mar, qoqar")
