import pandas as pd


def apply_transform(s: pd.Series, transform: str) -> pd.Series:
    """Apply a named transform to a date-indexed Series.

    Supported transforms:
        level  — return as-is
        yoy    — year-over-year % change: (v / v.shift(12) - 1) * 100
        mom    — month-over-month % change: (v / v.shift(1) - 1) * 100
    """
    if transform == "level":
        return s
    if transform == "yoy":
        return (s / s.shift(12) - 1) * 100
    if transform == "mom":
        return (s / s.shift(1) - 1) * 100
    raise ValueError(f"Unknown transform '{transform}'. Choose from: level, yoy, mom")
