"""Command-line entry point for csv-diff-cli."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from csv_diff.diff import diff_csv, summarize_diff
from csv_diff.filter import FilterError, parse_columns, validate_columns
from csv_diff.formatter import format_diff
from csv_diff.reader import CSVReadError, get_key_column, read_csv
from csv_diff.sorter import SortError, parse_sort_key, sort_diff
from csv_diff.stats import compute_stats, format_stats


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and show human-readable diffs.",
    )
    parser.add_argument("file_a", help="First (old) CSV file")
    parser.add_argument("file_b", help="Second (new) CSV file")
    parser.add_argument(
        "--key", "-k", default=None, help="Column to use as row key"
    )
    parser.add_argument(
        "--delimiter", "-d", default=",", help="CSV delimiter (default: comma)"
    )
    parser.add_argument(
        "--columns",
        "-c",
        default=None,
        help="Comma-separated list of columns to include in diff",
    )
    parser.add_argument(
        "--sort",
        "-s",
        default=None,
        choices=["key", "type"],
        help="Sort output by 'key' or 'type'",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Print a summary statistics block after the diff",
    )
    return parser


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    parser = build_parser()
    args: Namespace = parser.parse_args(argv)

    try:
        rows_a = read_csv(args.file_a, delimiter=args.delimiter)
        rows_b = read_csv(args.file_b, delimiter=args.delimiter)
    except CSVReadError as exc:
        print(f"Error reading CSV: {exc}", file=sys.stderr)
        return 2

    key_col = get_key_column(rows_a, args.key)

    try:
        columns = parse_columns(args.columns)
        if columns:
            all_headers = list(rows_a[0].keys()) if rows_a else []
            validate_columns(columns, all_headers)
    except FilterError as exc:
        print(f"Column filter error: {exc}", file=sys.stderr)
        return 2

    try:
        sort_key = parse_sort_key(args.sort)
    except SortError as exc:
        print(f"Sort error: {exc}", file=sys.stderr)
        return 2

    diff = diff_csv(rows_a, rows_b, key_col=key_col, columns=columns)
    diff = sort_diff(diff, sort_key)

    output = format_diff(diff)
    if output:
        print(output)

    if args.stats:
        total = max(len(rows_a), len(rows_b))
        stats = compute_stats(diff, total_rows=total)
        print(format_stats(stats))

    return 1 if diff else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
