"""Compute column-change correlation across diff events."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from csv_diff.diff import RowModified


class CorrelationError(Exception):
    """Raised when correlation computation fails."""


@dataclass
class ColumnPair:
    col_a: str
    col_b: str
    co_changes: int = 0

    @property
    def key(self) -> tuple:
        return (self.col_a, self.col_b)


@dataclass
class CorrelationResult:
    pairs: Dict[tuple, ColumnPair] = field(default_factory=dict)
    total_modified: int = 0


def parse_correlation_columns(value: Optional[str]) -> Optional[List[str]]:
    """Parse a comma-separated list of columns to correlate."""
    if not value or not value.strip():
        return None
    parts = [p.strip() for p in value.split(",")]
    if any(p == "" for p in parts):
        raise CorrelationError("Column list contains empty entry")
    return parts


def validate_correlation_columns(columns: List[str], headers: List[str]) -> None:
    """Raise CorrelationError if any column is not in headers."""
    missing = [c for c in columns if c not in headers]
    if missing:
        raise CorrelationError(f"Unknown columns: {', '.join(missing)}")


def compute_correlation(
    events: Sequence,
    columns: Optional[List[str]] = None,
) -> CorrelationResult:
    """Count how often pairs of columns change together in RowModified events."""
    result = CorrelationResult()
    for event in events:
        if not isinstance(event, RowModified):
            continue
        result.total_modified += 1
        changed = [
            col
            for col, (old, new) in event.changes.items()
            if old != new and (columns is None or col in columns)
        ]
        for i, col_a in enumerate(changed):
            for col_b in changed[i + 1 :]:
                a, b = (col_a, col_b) if col_a <= col_b else (col_b, col_a)
                key = (a, b)
                if key not in result.pairs:
                    result.pairs[key] = ColumnPair(col_a=a, col_b=b)
                result.pairs[key].co_changes += 1
    return result


def format_correlation(result: CorrelationResult) -> str:
    """Return a human-readable summary of column-change correlations."""
    lines = ["=== Column Change Correlation ==="]
    if not result.pairs:
        lines.append("  No co-changing column pairs found.")
        return "\n".join(lines)
    sorted_pairs = sorted(result.pairs.values(), key=lambda p: -p.co_changes)
    lines.append(f"  {'Column A':<20} {'Column B':<20} {'Co-changes':>10}")
    lines.append("  " + "-" * 52)
    for pair in sorted_pairs:
        lines.append(f"  {pair.col_a:<20} {pair.col_b:<20} {pair.co_changes:>10}")
    return "\n".join(lines)
