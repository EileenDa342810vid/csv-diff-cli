"""CLI helpers for the quorum feature."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .quorum import QuorumError, QuorumResult, format_quorum, parse_quorum


def add_quorum_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --quorum flag on *parser*."""
    parser.add_argument(
        "--quorum",
        metavar="N",
        default=None,
        help=(
            "When combining multiple diffs, only emit events agreed upon by "
            "at least N sources (default: 1, i.e. any event passes)."
        ),
    )
    parser.add_argument(
        "--quorum-only",
        action="store_true",
        default=False,
        help="Print quorum report and suppress the normal diff output.",
    )


def resolve_quorum(args: argparse.Namespace) -> Optional[int]:
    """Parse and validate the --quorum argument, exit on error."""
    raw = getattr(args, "quorum", None)
    if raw is None:
        return None
    try:
        return parse_quorum(raw)
    except QuorumError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)


def maybe_print_quorum(
    args: argparse.Namespace,
    result: QuorumResult,
) -> bool:
    """Print quorum report when --quorum-only is set.

    Returns True if the caller should suppress normal output.
    """
    if not getattr(args, "quorum_only", False):
        return False
    print(format_quorum(result))
    return True
