"""Command-line interface for csv-diff-cli."""

import argparse
import sys

from csv_diff.diff import diff_csv, summarize_diff
from csv_diff.filter import FilterError, parse_columns
from csv_diff.formatter import format_diff
from csv_diff.reader import CSVReadError, get_key_column, read_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and show human-readable diffs.",
    )
    parser.add_argument("old_file", help="Original CSV file")
    parser.add_argument("new_file", help="New CSV file")
    parser.add_argument(
        "--key",
        default=None,
        help="Column to use as the unique row key (default: first column)",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="CSV delimiter character (default: ',')",
    )
    parser.add_argument(
        "--columns",
        default=None,
        help="Comma-separated list of columns to compare (default: all)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        old_rows, old_headers = read_csv(args.old_file, delimiter=args.delimiter)
        new_rows, new_headers = read_csv(args.new_file, delimiter=args.delimiter)
    except CSVReadError as exc:
        print(f"Error reading CSV: {exc}", file=sys.stderr)
        return 2

    key_column = args.key or get_key_column(old_headers)

    try:
        columns = parse_columns(args.columns)
    except FilterError as exc:
        print(f"Filter error: {exc}", file=sys.stderr)
        return 2

    try:
        results = diff_csv(old_rows, new_rows, key_column=key_column, columns=columns)
    except (FilterError, KeyError) as exc:
        print(f"Diff error: {exc}", file=sys.stderr)
        return 2

    if not results:
        print("No differences found.")
        return 0

    output = format_diff(results, use_color=not args.no_color)
    print(output)

    summary = summarize_diff(results)
    print(
        f"\nSummary: {summary['added']} added, "
        f"{summary['removed']} removed, "
        f"{summary['modified']} modified."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
