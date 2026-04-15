"""Command-line entry point for csv-diff-cli."""

from __future__ import annotations

import argparse
import sys

from csv_diff.reader import read_csv, get_key_column, CSVReadError
from csv_diff.diff import diff_csv
from csv_diff.formatter import format_diff
from csv_diff.filter import parse_columns, validate_columns, filter_rows, FilterError
from csv_diff.sorter import parse_sort_key, sort_diff, SortError
from csv_diff.stats import compute_stats, format_stats, has_changes
from csv_diff.pager import should_page, page_output
from csv_diff.color import _colour_enabled
from csv_diff.truncate import parse_max_width, TruncateError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and show human-readable diffs.",
    )
    parser.add_argument("file_a", help="Original CSV file")
    parser.add_argument("file_b", help="Modified CSV file")
    parser.add_argument("--key", default=None, help="Column to use as the row key")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
    parser.add_argument("--columns", default=None, help="Comma-separated list of columns to compare")
    parser.add_argument("--sort", default=None, choices=["key", "type"], help="Sort diff output")
    parser.add_argument("--stats", action="store_true", help="Print summary statistics")
    parser.add_argument("--pager", action="store_true", default=False, help="Force pager")
    parser.add_argument("--no-pager", action="store_true", default=False, help="Disable pager")
    parser.add_argument("--color", action="store_true", default=False, help="Force colour output")
    parser.add_argument("--no-color", action="store_true", default=False, help="Disable colour output")
    parser.add_argument(
        "--max-width",
        default=None,
        dest="max_width",
        help="Truncate cell values to this many characters",
    )
    return parser


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    parser = build_parser()
    args = parser.parse_args(argv)

    # Resolve max-width early so we can emit parser errors.
    try:
        max_width = parse_max_width(args.max_width)
    except TruncateError as exc:
        parser.error(str(exc))

    try:
        rows_a = read_csv(args.file_a, delimiter=args.delimiter)
        rows_b = read_csv(args.file_b, delimiter=args.delimiter)
    except CSVReadError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    key = get_key_column(rows_a, args.key)

    try:
        columns = parse_columns(args.columns)
        if columns is not None:
            validate_columns(columns, rows_a)
        rows_a = filter_rows(rows_a, columns)
        rows_b = filter_rows(rows_b, columns)
    except FilterError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    diff = diff_csv(rows_a, rows_b, key=key)

    try:
        sort_key = parse_sort_key(args.sort)
        diff = sort_diff(diff, sort_key)
    except SortError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    use_color = _colour_enabled(force=args.color, disable=args.no_color)
    output = format_diff(diff, color=use_color, max_width=max_width)

    if args.stats:
        stats = compute_stats(diff)
        output = output + "\n\n" + format_stats(stats)

    use_pager = should_page(force=args.pager, disable=args.no_pager)
    if use_pager:
        page_output(output)
    else:
        print(output)

    return 1 if has_changes(diff) else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
