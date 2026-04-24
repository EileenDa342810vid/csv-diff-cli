"""CLI helpers for duplicate-row detection."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .dedupe import DedupeError, find_duplicates, format_duplicates


def add_dedupe_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --dedupe flag on *parser*."""
    parser.add_argument(
        "--dedupe",
        action="store_true",
        default=False,
        help="report duplicate keys found in either input file and exit non-zero if any are found",
    )


def maybe_report_duplicates(
    args: argparse.Namespace,
    rows_a: List[dict],
    rows_b: List[dict],
    key_column: str,
) -> bool:
    """If --dedupe was requested, print duplicate groups and return True.

    Exits with code 2 on error, code 1 when duplicates are found,
    code 0 when both files are clean.
    Returns False when --dedupe was not requested so the caller can
    continue with normal diff processing.
    """
    if not getattr(args, "dedupe", False):
        return False

    try:
        dupes_a = find_duplicates(rows_a, key_column)
        dupes_b = find_duplicates(rows_b, key_column)
    except DedupeError as exc:
        print(f"dedupe error: {exc}", file=sys.stderr)
        sys.exit(2)

    report_a = format_duplicates(dupes_a, label="file-a")
    report_b = format_duplicates(dupes_b, label="file-b")

    found = False
    if report_a:
        print(report_a)
        found = True
    if report_b:
        print(report_b)
        found = True

    if not found:
        print("No duplicate keys found.")

    sys.exit(1 if found else 0)
