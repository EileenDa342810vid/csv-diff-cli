"""Cadence analysis: detect how frequently rows change between two CSVs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class CadenceError(Exception):
    """Raised when cadence analysis fails."""


@dataclass
class CadenceResult:
    total_rows: int
    changed_rows: int
    change_rate: float  # 0.0 – 1.0
    grade: str          # HIGH / MEDIUM / LOW / NONE
    column_rates: dict = field(default_factory=dict)  # col -> rate


def parse_cadence_column(value: Optional[str]) -> Optional[str]:
    """Return stripped column name or None."""
    if not value or not value.strip():
        return None
    return value.strip()


def _grade(rate: float) -> str:
    if rate == 0.0:
        return "NONE"
    if rate < 0.25:
        return "LOW"
    if rate < 0.75:
        return "MEDIUM"
    return "HIGH"


def compute_cadence(
    diff: list,
    total_rows: int,
    focus_column: Optional[str] = None,
) -> CadenceResult:
    """Compute change cadence from a diff list.

    Args:
        diff: list of RowAdded / RowRemoved / RowModified events.
        total_rows: number of rows in the *larger* of the two files.
        focus_column: if given, also compute per-column rate for that column.
    """
    if total_rows < 0:
        raise CadenceError("total_rows must be non-negative")

    changed: set = set()
    col_changed: set = set()

    for i, event in enumerate(diff):
        if isinstance(event, (RowAdded, RowRemoved)):
            changed.add(i)
            if focus_column is not None:
                row = event.row if isinstance(event, RowAdded) else event.row
                if focus_column in row:
                    col_changed.add(i)
        elif isinstance(event, RowModified):
            changed.add(i)
            if focus_column is not None and focus_column in event.differences:
                col_changed.add(i)

    n_changed = len(changed)
    rate = (n_changed / total_rows) if total_rows > 0 else 0.0

    col_rates: dict = {}
    if focus_column is not None:
        col_rate = (len(col_changed) / total_rows) if total_rows > 0 else 0.0
        col_rates[focus_column] = round(col_rate, 4)

    return CadenceResult(
        total_rows=total_rows,
        changed_rows=n_changed,
        change_rate=round(rate, 4),
        grade=_grade(rate),
        column_rates=col_rates,
    )


def format_cadence(result: CadenceResult) -> str:
    """Return a human-readable cadence report."""
    lines = [
        "=== Change Cadence ===",
        f"Total rows   : {result.total_rows}",
        f"Changed rows : {result.changed_rows}",
        f"Change rate  : {result.change_rate:.1%}",
        f"Grade        : {result.grade}",
    ]
    if result.column_rates:
        lines.append("Column rates :")
        for col, rate in result.column_rates.items():
            lines.append(f"  {col}: {rate:.1%}")
    return "\n".join(lines)
