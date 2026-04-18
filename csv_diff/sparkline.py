"""Generate ASCII sparklines from numeric diff column values."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved

SPARK_CHARS = " ▁▂▃▄▅▆▇█"


class SparklineError(ValueError):
    pass


@dataclass
class SparklineResult:
    column: str
    values: List[float]
    line: str


def parse_sparkline_column(value: Optional[str]) -> Optional[str]:
    if not value or not value.strip():
        return None
    return value.strip()


def _extract_values(events: list, column: str) -> List[float]:
    values: List[float] = []
    for event in events:
        row = None
        if isinstance(event, RowAdded):
            row = event.row
        elif isinstance(event, RowRemoved):
            row = event.row
        elif isinstance(event, RowModified):
            row = event.new_row
        if row is None or column not in row:
            continue
        try:
            values.append(float(row[column]))
        except (ValueError, TypeError):
            pass
    return values


def _render(values: List[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo or 1.0
    chars = []
    for v in values:
        idx = int((v - lo) / span * (len(SPARK_CHARS) - 1))
        chars.append(SPARK_CHARS[idx])
    return "".join(chars)


def compute_sparkline(events: list, column: str) -> SparklineResult:
    values = _extract_values(events, column)
    if not values:
        raise SparklineError(f"No numeric data found for column '{column}'")
    return SparklineResult(column=column, values=values, line=_render(values))


def format_sparkline(result: SparklineResult) -> str:
    lo = min(result.values)
    hi = max(result.values)
    return (
        f"Sparkline [{result.column}]: {result.line}  "
        f"(n={len(result.values)}, min={lo:.4g}, max={hi:.4g})"
    )
