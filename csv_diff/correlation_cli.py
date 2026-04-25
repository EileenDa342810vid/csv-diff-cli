"""CLI integration for column-change correlation."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Sequence

from csv_diff.correlation import (
    CorrelationError,
    compute_correlation,
    format_correlation,
    parse_correlation_columns,
    validate_correlation_columns,
)


def add_correlation_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --correlate and --correlate-only flags on *parser*."""
    parser.add_argument(
        "--correlate",
        metavar="COLUMNS",
        default=None,
        help="Comma-separated columns to include in correlation analysis (default: all).",
    )
    parser.add_argument(
        "--correlate-only",
        action="store_true",
        default=False,
        help="Print correlation report and exit without showing the diff.",
    )


def maybe_print_correlation(
    args: argparse.Namespace,
    events: Sequence,
    headers: List[str],
) -> bool:
    """Print correlation report if requested.  Returns True when --correlate-only is set."""
    if not getattr(args, "correlate", None) and not getattr(args, "correlate_only", False):
        return False

    try:
        columns: Optional[list] = parse_correlation_columns(getattr(args, "correlate", None))
        if columns is not None:
            validate_correlation_columns(columns, headers)
    except CorrelationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    result = compute_correlation(events, columns)
    print(format_correlation(result))
    return bool(getattr(args, "correlate_only", False))
