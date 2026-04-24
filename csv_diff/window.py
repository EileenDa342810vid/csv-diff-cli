"""Sliding-window aggregation over numeric diff values.

Provides a way to compute rolling statistics (mean, min, max) for a numeric
column across the changed rows in a diff result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class WindowError(ValueError):
    """Raised when window configuration is invalid."""


@dataclass(frozen=True)
class WindowResult:
    column: str
    window_size: int
    values: List[float]
    means: List[float]
    mins: List[float]
    maxs: List[float]


def parse_window_size(value: object) -> Optional[int]:
    """Return *value* as a positive int, or None when value is None."""
    if value is None:
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise WindowError(f"Window size must be an integer, got {value!r}")
    if n < 1:
        raise WindowError(f"Window size must be >= 1, got {n}")
    return n


def _extract_numeric_values(
    events: Sequence[object], column: str
) -> List[float]:
    """Pull float values for *column* from added/removed/modified events."""
    results: List[float] = []
    for event in events:
        row: Optional[dict] = None
        if isinstance(event, RowAdded):
            row = event.row
        elif isinstance(event, RowRemoved):
            row = event.row
        elif isinstance(event, RowModified):
            row = event.new_row
        if row is None:
            continue
        raw = row.get(column)
        if raw is None:
            continue
        try:
            results.append(float(raw))
        except (TypeError, ValueError):
            pass
    return results


def compute_window(
    events: Sequence[object], column: str, window_size: int
) -> WindowResult:
    """Compute rolling mean/min/max over *column* with the given window."""
    values = _extract_numeric_values(events, column)
    means: List[float] = []
    mins: List[float] = []
    maxs: List[float] = []
    for i in range(len(values)):
        start = max(0, i - window_size + 1)
        window = values[start : i + 1]
        means.append(sum(window) / len(window))
        mins.append(min(window))
        maxs.append(max(window))
    return WindowResult(
        column=column,
        window_size=window_size,
        values=values,
        means=means,
        mins=mins,
        maxs=maxs,
    )


def format_window(result: WindowResult) -> str:
    """Return a human-readable summary of the window result."""
    if not result.values:
        return f"window({result.column}, {result.window_size}): no numeric data"
    lines = [
        f"window({result.column}, size={result.window_size})",
        f"  points : {len(result.values)}",
        f"  overall mean : {sum(result.means) / len(result.means):.4g}",
        f"  overall min  : {min(result.mins):.4g}",
        f"  overall max  : {max(result.maxs):.4g}",
    ]
    return "\n".join(lines)
