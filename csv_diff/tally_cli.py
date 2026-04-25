"""CLI integration for the tally feature."""
from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional, Union

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.tally import (
    ColumnTally,
    TallyError,
    format_tally,
    parse_tally_columns,
    tally_diff,
    validate_tally_columns,
)

DiffEvent = Union[RowAdded, RowRemoved, RowModified]


def add_tally_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --tally flag on *parser*."""
    parser.add_argument(
        "--tally",
        metavar="COLUMNS",
        default=None,
        help=(
            "Comma-separated list of columns whose changed values should be "
            "tallied and printed after the diff output."
        ),
    )


def maybe_print_tally(
    args: argparse.Namespace,
    events: List[DiffEvent],
    headers: List[str],
) -> bool:
    """Compute and print tally if --tally was requested.

    Returns True when tally output was produced, False otherwise.
    Calls sys.exit(2) on bad column names.
    """
    raw: Optional[str] = getattr(args, "tally", None)
    if not raw:
        return False

    try:
        columns = parse_tally_columns(raw)
    except TallyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    if columns is None:
        return False

    try:
        validate_tally_columns(columns, headers)
    except TallyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    tallies: Dict[str, ColumnTally] = tally_diff(events, columns)
    print(format_tally(tallies))
    return True
