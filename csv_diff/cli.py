"""Command-line interface for csv-diff-cli."""

import argparse
import sys

from csv_diff.diff import diff_csv
from csv_diff.formatter import format_diff
from csv_diff.reader import CSVReadError, get_key_column, read_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and display human-readable diffs.",
    )
    parser.add_argument("file_a", help="Original CSV file")
    parser.add_argument("file_b", help="Modified CSV file")
    parser.add_argument(
        "-k",
        "--key",
        metavar="COLUMN",
        default=None,
        help="Column name to use as the row key (default: first column)",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        metavar="CHAR",
        default=",",
        help="Field delimiter character (default: ',')",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows_a = read_csv(args.file_a, delimiter=args.delimiter)
        rows_b = read_csv(args.file_b, delimiter=args.delimiter)
    except CSVReadError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 1

    try:
        key_column = get_key_column(rows_a, args.key)
    except (KeyError, ValueError) as exc:
        print(f"Error determining key column: {exc}", file=sys.stderr)
        return 1

    changes = diff_csv(rows_a, rows_b, key_column=key_column)
    output = format_diff(changes, use_color=not args.no_color)

    if output:
        print(output)
        return 1  # non-zero exit when differences exist

    print("No differences found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
