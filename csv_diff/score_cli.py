"""CLI helpers for the --score flag."""
from __future__ import annotations

import argparse
from typing import List

from csv_diff.score import ScoreError, compute_score, format_score


def add_score_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--score",
        action="store_true",
        default=False,
        help="Print a similarity score after the diff.",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        default=False,
        help="Print only the similarity score and suppress the diff output.",
    )


def maybe_print_score(args: argparse.Namespace, diff: list, total_rows: int) -> bool:
    """Print score if requested.  Returns True if score-only mode is active."""
    if not (args.score or args.score_only):
        return False
    try:
        s = compute_score(diff, total_rows)
    except ScoreError as exc:
        import sys
        print(f"score error: {exc}", file=sys.stderr)
        sys.exit(2)
    print(format_score(s))
    return bool(args.score_only)
