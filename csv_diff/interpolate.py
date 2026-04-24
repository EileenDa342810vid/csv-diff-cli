"""Numeric interpolation for missing values in diff rows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


class InterpolateError(Exception):
    """Raised when interpolation configuration is invalid."""


@dataclass(frozen=True)
class InterpolateConfig:
    columns: List[str]
    fill_value: float


def parse_interpolate_columns(value: Optional[str]) -> Optional[List[str]]:
    """Parse a comma-separated list of column names to interpolate."""
    if not value or not value.strip():
        return None
    parts = [p.strip() for p in value.split(",")]
    for part in parts:
        if not part:
            raise InterpolateError("Empty column entry in interpolate spec.")
    return parts


def parse_fill_value(value: Optional[str]) -> float:
    """Parse the numeric fill value (default 0.0)."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except ValueError:
        raise InterpolateError(f"Fill value must be numeric, got: {value!r}")


def validate_interpolate_columns(columns: List[str], headers: List[str]) -> None:
    """Ensure all requested columns exist in the CSV headers."""
    missing = [c for c in columns if c not in headers]
    if missing:
        raise InterpolateError(
            f"Interpolate columns not found in headers: {', '.join(missing)}"
        )


def interpolate_row(row: Dict[str, str], columns: List[str], fill: float) -> Dict[str, str]:
    """Return a copy of *row* with blank values in *columns* replaced by *fill*."""
    result = dict(row)
    for col in columns:
        if col in result and result[col].strip() == "":
            result[col] = str(fill)
    return result


def interpolate_rows(
    rows: List[Dict[str, str]],
    columns: List[str],
    fill: float = 0.0,
) -> List[Dict[str, str]]:
    """Apply interpolation to every row in *rows*."""
    return [interpolate_row(r, columns, fill) for r in rows]
