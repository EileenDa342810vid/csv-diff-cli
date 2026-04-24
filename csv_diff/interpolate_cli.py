"""CLI helpers for the --interpolate feature."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Dict

from csv_diff.interpolate import (
    InterpolateError,
    parse_fill_value,
    parse_interpolate_columns,
    validate_interpolate_columns,
    interpolate_rows,
)


def add_interpolate_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --interpolate and --fill-value flags on *parser*."""
    parser.add_argument(
        "--interpolate",
        metavar="COLUMNS",
        default=None,
        help="Comma-separated columns whose blank values should be filled.",
    )
    parser.add_argument(
        "--fill-value",
        metavar="NUMBER",
        default=None,
        help="Numeric value used to fill blanks (default: 0).",
    )


def resolve_interpolate(
    args: argparse.Namespace,
    headers: List[str],
    rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Apply interpolation to *rows* based on CLI args; return (possibly unchanged) rows."""
    columns_raw: Optional[str] = getattr(args, "interpolate", None)
    fill_raw: Optional[str] = getattr(args, "fill_value", None)

    if columns_raw is None:
        return rows

    try:
        columns = parse_interpolate_columns(columns_raw)
        fill = parse_fill_value(fill_raw)
        if columns:
            validate_interpolate_columns(columns, headers)
            return interpolate_rows(rows, columns, fill)
    except InterpolateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    return rows
