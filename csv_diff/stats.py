"""Statistics and summary reporting for CSV diffs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved


@dataclass
class DiffStats:
    """Aggregated statistics about a diff result."""

    added: int = 0
    removed: int = 0
    modified: int = 0
    unchanged: int = 0
    modified_columns: dict[str, int] = field(default_factory=dict)

    @property
    def total_changes(self) -> int:
        return self.added + self.removed + self.modified

    @property
    def has_changes(self) -> bool:
        return self.total_changes > 0


def compute_stats(
    diff: Sequence[RowAdded | RowRemoved | RowModified],
    total_rows: int = 0,
) -> DiffStats:
    """Compute statistics from a list of diff events."""
    stats = DiffStats()

    for event in diff:
        if isinstance(event, RowAdded):
            stats.added += 1
        elif isinstance(event, RowRemoved):
            stats.removed += 1
        elif isinstance(event, RowModified):
            stats.modified += 1
            for col in event.changes:
                stats.modified_columns[col] = stats.modified_columns.get(col, 0) + 1

    changes = stats.added + stats.removed + stats.modified
    stats.unchanged = max(0, total_rows - changes)
    return stats


def format_stats(stats: DiffStats) -> str:
    """Return a human-readable summary string for the given stats."""
    lines: list[str] = []
    lines.append("=== Diff Summary ===")
    if not stats.has_changes:
        lines.append("No differences found.")
        return "\n".join(lines)

    lines.append(f"  Added rows   : {stats.added}")
    lines.append(f"  Removed rows : {stats.removed}")
    lines.append(f"  Modified rows: {stats.modified}")
    if stats.unchanged:
        lines.append(f"  Unchanged    : {stats.unchanged}")

    if stats.modified_columns:
        lines.append("  Most-changed columns:")
        for col, count in sorted(
            stats.modified_columns.items(), key=lambda kv: -kv[1]
        ):
            lines.append(f"    {col}: {count} change(s)")

    return "\n".join(lines)
