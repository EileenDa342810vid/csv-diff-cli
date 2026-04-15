"""Command-line entry point for csv-diff-cli."""

from __future__ import annotations

import sys
import argparse
from typing import List, Optional

from csv_diff.reader import read_csv, get_key_column, CSVReadError
from csv_diff.diff import diff_csv, summarize_diff
from csv_diff.formatter import format_diff
from csv_diff.filter import parse_columns, validate_columns, filter_rows, FilterError
from csv_diff.sorter import parse_sort_key, sort_diff, SortError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and show human-readable diffs.",
    )
    parser.add_argument("file_a", help="Original CSV file")
    parser.add_argument("file_b", help="Modified CSV file")
    parser.add_argument(
        "--key",
        default=None,
        help="Column to use as the row identifier (default: first column)",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="CSV field delimiter (default: ',')",
    )
    parser.add_argument(
        "--columns",
        default=None,
        help="Comma-separated list of columns to compare",
    )
    parser.add_argument(
        "--sort",
        default=None,
        metavar="KEY",
        help="Sort output by: key, type, or column",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line instead of full diff",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:  # noqa: C901
    parser = build_parser()
    args = parser.parse_args(argv)

    # --- validate sort key early so we fail fast ---
    try:
        sort_key = parse_sort_key(args.sort)
    except SortError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        rows_a = read_csv(args.file_a, delimiter=args.delimiter)
        rows_b = read_csv(args.file_b, delimiter=args.delimiter)
    except CSVReadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not rows_a and not rows_b:
        return 0

    headers = list(rows_a[0].keys()) if rows_a else list(rows_b[0].keys())

    try:
        columns = parse_columns(args.columns)
        if columns is not None:
            validate_columns(columns, headers)
        rows_a = filter_rows(rows_a, columns)
        rows_b = filter_rows(rows_b, columns)
    except FilterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    key_col = get_key_column(rows_a or rows_b, args.key)
    changes = diff_csv(rows_a, rows_b, key_column=key_col)
    changes = sort_diff(changes, sort_key)

    if args.summary:
        print(summarize_diff(changes))
    else:
        output = format_diff(changes, key_column=key_col)
        if output:
            print(output)

    return 0 if not changes else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
