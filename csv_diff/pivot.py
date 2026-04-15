"""Pivot diff results by column for column-centric reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class PivotError(Exception):
    """Raised when pivot operations fail."""


@dataclass
class ColumnPivot:
    """Aggregated change information for a single column."""

    column: str
    added_values: List[str] = field(default_factory=list)
    removed_values: List[str] = field(default_factory=list)
    modified_pairs: List[tuple[str, str]] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added_values) + len(self.removed_values) + len(self.modified_pairs)


def pivot_by_column(
    diff: List, headers: Optional[List[str]] = None
) -> Dict[str, ColumnPivot]:
    """Group diff events by the column(s) they affect.

    Args:
        diff: List of RowAdded, RowRemoved, or RowModified events.
        headers: Optional explicit column list; inferred from events when absent.

    Returns:
        Mapping of column name -> ColumnPivot.

    Raises:
        PivotError: If diff contains an unrecognised event type.
    """
    pivots: Dict[str, ColumnPivot] = {}

    def _get(col: str) -> ColumnPivot:
        if col not in pivots:
            pivots[col] = ColumnPivot(column=col)
        return pivots[col]

    for event in diff:
        if isinstance(event, RowAdded):
            for col, val in event.row.items():
                _get(col).added_values.append(val)
        elif isinstance(event, RowRemoved):
            for col, val in event.row.items():
                _get(col).removed_values.append(val)
        elif isinstance(event, RowModified):
            changed_cols = {
                col
                for col in event.old_row
                if event.old_row.get(col) != event.new_row.get(col)
            }
            for col in changed_cols:
                _get(col).modified_pairs.append(
                    (event.old_row.get(col, ""), event.new_row.get(col, ""))
                )
        else:
            raise PivotError(f"Unrecognised diff event type: {type(event).__name__}")

    return pivots


def format_pivot(pivots: Dict[str, ColumnPivot]) -> str:
    """Render a column-pivot summary as a human-readable string."""
    if not pivots:
        return "No column changes."

    lines: List[str] = []
    for col, cp in sorted(pivots.items()):
        lines.append(f"Column '{col}': {cp.total_changes} change(s)")
        for val in cp.added_values:
            lines.append(f"  + {val}")
        for val in cp.removed_values:
            lines.append(f"  - {val}")
        for old, new in cp.modified_pairs:
            lines.append(f"  ~ {old!r} -> {new!r}")
    return "\n".join(lines)
