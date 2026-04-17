"""Rollup: aggregate diff events by a numeric column."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class RollupError(Exception):
    pass


@dataclass
class ColumnRollup:
    column: str
    total_added: float = 0.0
    total_removed: float = 0.0
    total_delta: float = 0.0
    changed_rows: int = 0


def parse_rollup_column(value: Optional[str]) -> Optional[str]:
    if not value or not value.strip():
        return None
    return value.strip()


def _get_float(row: dict, column: str) -> float:
    try:
        return float(row.get(column, 0) or 0)
    except (ValueError, TypeError):
        return 0.0


def rollup_diff(events: list, column: str) -> ColumnRollup:
    result = ColumnRollup(column=column)
    for event in events:
        if isinstance(event, RowAdded):
            v = _get_float(event.row, column)
            result.total_added += v
            result.total_delta += v
            result.changed_rows += 1
        elif isinstance(event, RowRemoved):
            v = _get_float(event.row, column)
            result.total_removed += v
            result.total_delta -= v
            result.changed_rows += 1
        elif isinstance(event, RowModified):
            old = _get_float(event.old_row, column)
            new = _get_float(event.new_row, column)
            result.total_delta += new - old
            result.changed_rows += 1
    return result


def format_rollup(rollup: ColumnRollup) -> str:
    lines = [
        f"Rollup for column: {rollup.column}",
        f"  Added value   : {rollup.total_added:+.4g}",
        f"  Removed value : {rollup.total_removed:+.4g}",
        f"  Net delta     : {rollup.total_delta:+.4g}",
        f"  Changed rows  : {rollup.changed_rows}",
    ]
    return "\n".join(lines)
