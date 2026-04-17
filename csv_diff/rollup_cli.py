"""CLI helpers for the --rollup feature."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from typing import List

from csv_diff.rollup import RollupError, format_rollup, parse_rollup_column, rollup_diff


def add_rollup_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--rollup",
        metavar="COLUMN",
        default=None,
        help="Aggregate a numeric column across all diff events and print totals.",
    )


def maybe_print_rollup(args: Namespace, events: list, headers: List[str]) -> bool:
    column = parse_rollup_column(getattr(args, "rollup", None))
    if column is None:
        return False
    if column not in headers:
        print(f"error: rollup column '{column}' not found in headers", file=sys.stderr)
        sys.exit(2)
    try:
        rollup = rollup_diff(events, column)
        print(format_rollup(rollup))
    except RollupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    return True
