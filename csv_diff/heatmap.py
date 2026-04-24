"""Heatmap: compute change-frequency counts per (row_key, column) cell."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class HeatmapError(Exception):
    """Raised when heatmap computation fails."""


@dataclass
class HeatmapResult:
    """Stores per-column change counts across all diff events."""

    columns: List[str]
    counts: Dict[str, int] = field(default_factory=dict)

    def increment(self, column: str) -> None:
        self.counts[column] = self.counts.get(column, 0) + 1

    def total(self) -> int:
        return sum(self.counts.values())

    def hottest(self) -> Optional[str]:
        """Return the column with the most changes, or None if empty."""
        if not self.counts:
            return None
        return max(self.counts, key=lambda c: self.counts[c])


def compute_heatmap(
    events: Sequence,
    columns: List[str],
) -> HeatmapResult:
    """Count how many times each column appears in a change event.

    - RowAdded / RowRemoved: every column counts as changed.
    - RowModified: only columns whose old/new values differ count.
    """
    result = HeatmapResult(columns=list(columns))

    for event in events:
        if isinstance(event, (RowAdded, RowRemoved)):
            row = event.row
            for col in columns:
                if col in row:
                    result.increment(col)
        elif isinstance(event, RowModified):
            old, new = event.old_row, event.new_row
            for col in columns:
                if old.get(col) != new.get(col):
                    result.increment(col)

    return result


def format_heatmap(result: HeatmapResult) -> str:
    """Return a plain-text table of column change counts."""
    if not result.columns:
        return "(no columns)"

    lines: List[str] = ["Column Change Frequency:", "-" * 32]
    for col in result.columns:
        count = result.counts.get(col, 0)
        bar = "#" * min(count, 20)
        lines.append(f"  {col:<20} {count:>4}  {bar}")
    lines.append("-" * 32)
    lines.append(f"  {'TOTAL':<20} {result.total():>4}")
    return "\n".join(lines)
