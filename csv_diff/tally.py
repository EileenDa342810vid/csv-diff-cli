"""Tally changed values per column across all diff events."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from csv_diff.diff import RowAdded, RowModified, RowRemoved

DiffEvent = Union[RowAdded, RowRemoved, RowModified]


class TallyError(Exception):
    """Raised when tally computation fails."""


@dataclass
class ColumnTally:
    column: str
    unique_values: Dict[str, int] = field(default_factory=dict)

    def record(self, value: str) -> None:
        self.unique_values[value] = self.unique_values.get(value, 0) + 1

    @property
    def total(self) -> int:
        return sum(self.unique_values.values())

    @property
    def top(self) -> Optional[str]:
        if not self.unique_values:
            return None
        return max(self.unique_values, key=lambda k: self.unique_values[k])


def parse_tally_columns(value: Optional[str]) -> Optional[List[str]]:
    """Parse a comma-separated list of column names, or return None."""
    if not value or not value.strip():
        return None
    parts = [p.strip() for p in value.split(",")]
    if any(p == "" for p in parts):
        raise TallyError("Tally column list contains an empty entry")
    return parts


def validate_tally_columns(columns: List[str], headers: List[str]) -> None:
    """Raise TallyError if any requested column is absent from headers."""
    missing = [c for c in columns if c not in headers]
    if missing:
        raise TallyError(f"Unknown tally columns: {', '.join(missing)}")


def tally_diff(
    events: List[DiffEvent],
    columns: List[str],
) -> Dict[str, ColumnTally]:
    """Count how often each distinct value appears in *changed* cells."""
    tallies: Dict[str, ColumnTally] = {c: ColumnTally(column=c) for c in columns}

    for event in events:
        if isinstance(event, RowAdded):
            for col in columns:
                val = event.row.get(col, "")
                tallies[col].record(val)
        elif isinstance(event, RowRemoved):
            for col in columns:
                val = event.row.get(col, "")
                tallies[col].record(val)
        elif isinstance(event, RowModified):
            for col in columns:
                old = event.old_row.get(col, "")
                new = event.new_row.get(col, "")
                if old != new:
                    tallies[col].record(new)

    return tallies


def format_tally(tallies: Dict[str, ColumnTally]) -> str:
    """Return a human-readable summary of tally results."""
    if not tallies:
        return "Tally: no columns selected"
    lines = ["=== Value Tally ==="]
    for col, tally in tallies.items():
        lines.append(f"  {col}: {tally.total} change(s)")
        for val, count in sorted(tally.unique_values.items(), key=lambda x: -x[1]):
            lines.append(f"    {val!r}: {count}")
    return "\n".join(lines)
