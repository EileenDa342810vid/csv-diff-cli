"""CLI integration for column reordering."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Dict

from csv_diff.reorder import (
    ReorderError,
    ColumnOrder,
    parse_reorder_columns,
    validate_reorder_columns,
)


def add_reorder_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --reorder flag on *parser*."""
    parser.add_argument(
        "--reorder",
        metavar="COLS",
        default=None,
        help=(
            "Comma-separated list of columns to place first in diff output. "
            "Remaining columns follow in their original order."
        ),
    )


def resolve_reorder(
    args: argparse.Namespace, headers: List[str]
) -> Optional[ColumnOrder]:
    """Parse and validate the --reorder argument.

    Exits with code 2 on any error so the CLI surfaces a clean message.
    """
    spec: Optional[str] = getattr(args, "reorder", None)
    try:
        order = parse_reorder_columns(spec)
        if order is not None:
            validate_reorder_columns(order, headers)
        return order
    except ReorderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
