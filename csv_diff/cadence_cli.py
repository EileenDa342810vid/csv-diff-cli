"""CLI helpers for the --cadence feature."""
from __future__ import annotations

import sys
from typing import Optional

from csv_diff.cadence import CadenceError, compute_cadence, format_cadence, parse_cadence_column


def add_cadence_arguments(parser) -> None:  # type: ignore[type-arg]
    """Register --cadence and --cadence-column flags on *parser*."""
    parser.add_argument(
        "--cadence",
        action="store_true",
        default=False,
        help="Print a change-cadence report after the diff.",
    )
    parser.add_argument(
        "--cadence-column",
        metavar="COL",
        default=None,
        help="Also report the change rate for a specific column.",
    )


def maybe_print_cadence(
    args,  # type: ignore[type-arg]
    diff: list,
    total_rows: int,
) -> bool:
    """Print cadence report if ``--cadence`` was requested.

    Returns True if the report was printed, False otherwise.
    Exits with code 2 on configuration errors.
    """
    if not getattr(args, "cadence", False):
        return False

    focus: Optional[str] = parse_cadence_column(
        getattr(args, "cadence_column", None)
    )

    try:
        result = compute_cadence(diff, total_rows, focus_column=focus)
    except CadenceError as exc:
        print(f"cadence error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(format_cadence(result))
    return True
