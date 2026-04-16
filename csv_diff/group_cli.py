"""CLI helpers for --group-by support."""
from __future__ import annotations
from typing import Optional, List
import argparse

from csv_diff.group import (
    GroupError, parse_group_by, validate_group_column, group_diff, format_groups,
)
from csv_diff.diff import RowAdded, RowRemoved, RowModified

D RowRemoved | RowModified


def add_group_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--group-by",
        metavar="COLUMN",
        default=None,
        help="Group diff output by the values in COLUMN.",
    )


def maybe_print_groups(
    args: argparse.Namespace,
    events: List[DiffEvent],
    headers: List[str],
) -> bool:
    """Print grouped output if --group-by was requested.

    Returns True if grouping was performed so the caller can skip default output.
    """
    column = parse_group_by(getattr(args, "group_by", None))
    if column is None:
        return False
    try:
        validate_group_column(column, headers)
    except GroupError as exc:
        import sys
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    groups = group_diff(events, column)
    print(format_groups(groups, column))
    return True
