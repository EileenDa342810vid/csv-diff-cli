"""CLI helpers for the column-pivot / change-frequency report."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .pivot import PivotError, pivot_by_column, ColumnPivot


def add_pivot_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --pivot-by flag on *parser*."""
    parser.add_argument(
        "--pivot-by",
        metavar="COLUMN",
        default=None,
        help="Show a per-value change breakdown for COLUMN.",
    )


def maybe_print_pivot(
    args: argparse.Namespace,
    diff: list,
    headers: List[str],
) -> bool:
    """Print pivot table when --pivot-by is set.

    Returns True when output was printed so the caller can decide whether
    to suppress the normal diff output.
    """
    column: str | None = getattr(args, "pivot_by", None)
    if not column:
        return False

    if column not in headers:
        print(
            f"error: pivot column '{column}' not found in headers: {headers}",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        table: dict[str, ColumnPivot] = pivot_by_column(diff, column)
    except PivotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    _print_pivot_table(column, table)
    return True


def _print_pivot_table(column: str, table: dict[str, ColumnPivot]) -> None:
    print(f"Pivot by '{column}'")
    print(f"{'Value':<30} {'Added':>7} {'Removed':>9} {'Modified':>10} {'Total':>7}")
    print("-" * 67)
    if not table:
        print("  (no changes)")
        return
    for value, cp in sorted(table.items()):
        total = cp.added + cp.removed + cp.modified
        print(
            f"  {value:<28} {cp.added:>7} {cp.removed:>9} {cp.modified:>10} {total:>7}"
        )
