from pathlib import Path

import polars as pl


def read_csv(path: Path) -> pl.DataFrame:
    """Read a CSV file into a polars DataFrame."""
    return pl.read_csv(path)
