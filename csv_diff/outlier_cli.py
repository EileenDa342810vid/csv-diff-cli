"""CLI helpers for the --outlier-columns / --z-threshold flags."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, Optional, Sequence

from csv_diff.outlier import (
    OutlierError,
    OutlierResult,
    detect_outliers,
    format_outliers,
    parse_outlier_columns,
    parse_z_threshold,
)


def add_outlier_arguments(parser: ArgumentParser) -> None:
    """Register --outlier-columns and --z-threshold on *parser*."""
    parser.add_argument(
        "--outlier-columns",
        metavar="COLS",
        default=None,
        help="Comma-separated numeric columns to check for outliers.",
    )
    parser.add_argument(
        "--z-threshold",
        metavar="Z",
        type=float,
        default=None,
        help="Z-score threshold for outlier detection (default: 3.0).",
    )


def resolve_outliers(
    args: Namespace,
    events: Sequence,
    headers: Sequence[str],
) -> Optional[Dict[str, OutlierResult]]:
    """Parse CLI args and run outlier detection; return None when disabled."""
    try:
        columns = parse_outlier_columns(getattr(args, "outlier_columns", None))
    except OutlierError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    if columns is None:
        return None

    unknown = [c for c in columns if c not in headers]
    if unknown:
        print(
            f"error: unknown column(s) for --outlier-columns: {', '.join(unknown)}",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        z = parse_z_threshold(getattr(args, "z_threshold", None))
    except OutlierError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    return detect_outliers(events, columns, z)


def maybe_print_outliers(
    results: Optional[Dict[str, OutlierResult]],
) -> bool:
    """Print outlier summary if results are present.  Returns True when printed."""
    if results is None:
        return False
    text = format_outliers(results)
    if text:
        print(text)
    return True
