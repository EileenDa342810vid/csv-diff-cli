"""CLI helpers for the --velocity flag."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from csv_diff.velocity import (
    VelocityError,
    compute_velocity,
    format_velocity,
)


def add_velocity_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --velocity flag on *parser*."""
    parser.add_argument(
        "--velocity",
        action="store_true",
        default=False,
        help="Print a per-column change-velocity report.",
    )
    parser.add_argument(
        "--velocity-only",
        action="store_true",
        default=False,
        help="Print the velocity report and suppress the normal diff output.",
    )


def maybe_print_velocity(
    args: argparse.Namespace,
    events: list,
    headers: List[str],
) -> bool:
    """Print velocity report if requested.  Returns True when --velocity-only."""
    if not (args.velocity or args.velocity_only):
        return False

    try:
        result = compute_velocity(events, headers)
    except VelocityError as exc:
        print(f"velocity error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(format_velocity(result))
    return bool(args.velocity_only)
