"""Column-level change frequency summarization for CSV diffs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class SummarizeError(ValueError):
    """Raised when summarization cannot be completed."""


@dataclass
class ColumnFrequency:
    column: str
    change_count: int
    percentage: float


@dataclass
class ChangeSummary:
    total_rows_changed: int
    added: int
    removed: int
    modified: int
    column_frequencies: List[ColumnFrequency] = field(default_factory=list)


def compute_column_frequencies(
    diff: List,
    headers: Optional[List[str]] = None,
) -> Dict[str, int]:
    """Return a mapping of column name -> number of modifications touching that column."""
    counts: Counter = Counter()
    for event in diff:
        if isinstance(event, RowModified):
            for col in event.changes:
                counts[col] += 1
    return dict(counts)


def summarize_columns(
    diff: List,
    headers: Optional[List[str]] = None,
) -> ChangeSummary:
    """Build a ChangeSummary from a list of diff events."""
    added = sum(1 for e in diff if isinstance(e, RowAdded))
    removed = sum(1 for e in diff if isinstance(e, RowRemoved))
    modified = sum(1 for e in diff if isinstance(e, RowModified))
    total = added + removed + modified

    col_counts = compute_column_frequencies(diff, headers)

    frequencies: List[ColumnFrequency] = []
    for col, count in sorted(col_counts.items(), key=lambda x: -x[1]):
        pct = (count / modified * 100.0) if modified else 0.0
        frequencies.append(ColumnFrequency(column=col, change_count=count, percentage=round(pct, 1)))

    return ChangeSummary(
        total_rows_changed=total,
        added=added,
        removed=removed,
        modified=modified,
        column_frequencies=frequencies,
    )


def format_column_summary(summary: ChangeSummary) -> str:
    """Render a ChangeSummary as a human-readable string."""
    lines = [
        "=== Change Summary ===",
        f"  Rows added:    {summary.added}",
        f"  Rows removed:  {summary.removed}",
        f"  Rows modified: {summary.modified}",
        f"  Total changed: {summary.total_rows_changed}",
    ]
    if summary.column_frequencies:
        lines.append("  Modified columns (by frequency):")
        for cf in summary.column_frequencies:
            lines.append(f"    {cf.column}: {cf.change_count} ({cf.percentage}%)")
    return "\n".join(lines)
