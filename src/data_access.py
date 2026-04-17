import os
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_DEFAULT_RELATIVE_PATH = "../../haver-data"  # side-by-side repos under /workspaces


def get_haver_data_path() -> Path:
    """Return the haver-data repo root.

    Checks HAVER_DATA_REPO env var first; falls back to the default relative
    path that matches the standard Codespaces side-by-side workspace layout:
        /workspaces/haver-data
        /workspaces/monitoring-dashboard  ← this repo
    """
    raw = os.environ.get("HAVER_DATA_REPO")
    if raw:
        return Path(raw).expanduser().resolve()
    # Resolve relative to this file so it works regardless of cwd
    return (Path(__file__).parent / _DEFAULT_RELATIVE_PATH).resolve()


# ---------------------------------------------------------------------------
# File loaders
# ---------------------------------------------------------------------------

def _load_parquet(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Expected parquet file not found: {file_path}\n"
            "Set the HAVER_DATA_REPO environment variable to the correct path, e.g.:\n"
            "  export HAVER_DATA_REPO=/workspaces/haver-data"
        )
    return pd.read_parquet(file_path)


def load_data(haver_path: Path | None = None) -> pd.DataFrame:
    """Load data/data.parquet from the haver-data repo."""
    root = haver_path or get_haver_data_path()
    return _load_parquet(root / "data" / "data.parquet")


def load_metadata(haver_path: Path | None = None) -> pd.DataFrame:
    """Load data/metadata.parquet from the haver-data repo."""
    root = haver_path or get_haver_data_path()
    return _load_parquet(root / "data" / "metadata.parquet")


# ---------------------------------------------------------------------------
# Series loader
# ---------------------------------------------------------------------------

def load_series(code: str, haver_path: Path | None = None) -> pd.Series:
    """Return a date-indexed Series for one code (in code@database format).

    Raises KeyError if the code is not found in data.parquet.
    """
    df = load_data(haver_path)
    subset = df[df["code"] == code]
    if subset.empty:
        raise KeyError(f"Series '{code}' not found in data.parquet")
    return subset.set_index("date")["value"].sort_index()


# ---------------------------------------------------------------------------
# Availability checks (no exceptions)
# ---------------------------------------------------------------------------

def check_files(haver_path: Path | None = None) -> dict:
    """Return a dict with path and existence flags for each expected file."""
    root = haver_path or get_haver_data_path()
    return {
        "haver_data_path": root,
        "data_parquet": (root / "data" / "data.parquet").exists(),
        "metadata_parquet": (root / "data" / "metadata.parquet").exists(),
    }
