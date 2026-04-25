"""Compute change velocity: rate of changes per column over a diff."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff.diff import RowAdded, RowRemoved, RowModified


class VelocityError(Exception):
    """Raised when velocity computation fails."""


@dataclass
class ColumnVelocity:
    column: str
    changes: int = 0

    @property
    def rate(self) -> float:
        """Changes as a fraction of total rows examined (set externally)."""
        return self._rate

    def _set_rate(self, total: int) -> None:
        self._rate = self.changes / total if total > 0 else 0.0

    def __post_init__(self) -> None:
        self._rate: float = 0.0


@dataclass
class VelocityResult:
    columns: List[ColumnVelocity] = field(default_factory=list)
    total_rows: int = 0

    def fastest(self) -> Optional[ColumnVelocity]:
        return max(self.columns, key=lambda c: c.changes, default=None)


def parse_velocity_column(value: Optional[str]) -> Optional[str]:
    """Return stripped column name or None."""
    if not value or not value.strip():
        return None
    return value.strip()


def compute_velocity(
    events: list,
    headers: List[str],
) -> VelocityResult:
    """Count per-column changes across all diff events."""
    tally: Dict[str, int] = {h: 0 for h in headers}
    total = 0

    for event in events:
        total += 1
        if isinstance(event, RowAdded):
            for col in headers:
                if event.row.get(col, ""):
                    tally[col] += 1
        elif isinstance(event, RowRemoved):
            for col in headers:
                if event.row.get(col, ""):
                    tally[col] += 1
        elif isinstance(event, RowModified):
            for col in headers:
                if event.old_row.get(col) != event.new_row.get(col):
                    tally[col] += 1

    cols = [ColumnVelocity(column=h, changes=tally[h]) for h in headers]
    for c in cols:
        c._set_rate(total)

    return VelocityResult(columns=cols, total_rows=total)


def format_velocity(result: VelocityResult) -> str:
    """Return a human-readable velocity report."""
    lines = ["=== Change Velocity ==="]
    lines.append(f"Total rows examined: {result.total_rows}")
    lines.append(f"{'Column':<30} {'Changes':>8} {'Rate':>8}")
    lines.append("-" * 50)
    for col in sorted(result.columns, key=lambda c: c.changes, reverse=True):
        lines.append(f"{col.column:<30} {col.changes:>8} {col._rate:>7.1%}")
    return "\n".join(lines)
