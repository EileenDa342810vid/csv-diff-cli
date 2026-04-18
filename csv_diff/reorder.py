"""Column reordering support for csv-diff-cli."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


class ReorderError(ValueError):
    """Raised when a reorder specification is invalid."""


@dataclass
class ColumnOrder:
    columns: List[str]


def parse_reorder_columns(spec: Optional[str]) -> Optional[ColumnOrder]:
    """Parse a comma-separated list of column names into a ColumnOrder.

    Returns None if *spec* is None or empty.
    """
    if not spec or not spec.strip():
        return None
    parts = [p.strip() for p in spec.split(",")]
    empty = [p for p in parts if not p]
    if empty:
        raise ReorderError("reorder spec contains empty column entry")
    return ColumnOrder(columns=parts)


def validate_reorder_columns(order: ColumnOrder, headers: List[str]) -> None:
    """Raise ReorderError if any column in *order* is not present in *headers*."""
    missing = [c for c in order.columns if c not in headers]
    if missing:
        raise ReorderError(
            f"unknown column(s) in --reorder: {', '.join(missing)}"
        )


def apply_reorder(row: Dict[str, str], order: ColumnOrder) -> Dict[str, str]:
    """Return a new dict with keys arranged so that *order.columns* come first.

    Columns not listed in *order* are appended in their original relative order.
    """
    remaining = [k for k in row if k not in order.columns]
    new_keys = [c for c in order.columns if c in row] + remaining
    return {k: row[k] for k in new_keys}


def reorder_rows(
    rows: List[Dict[str, str]], order: Optional[ColumnOrder]
) -> List[Dict[str, str]]:
    """Apply *order* to every row; return rows unchanged when *order* is None."""
    if order is None:
        return rows
    return [apply_reorder(row, order) for row in rows]
