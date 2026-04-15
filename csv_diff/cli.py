"""Command-line entry point for csv-diff-cli."""
from __future__ import annotations

import sys
import argparse

from csv_diff.reader import read_csv, get_key_column, validate_matching_headers, CSVReadError
from csv_diff.diff import diff_csv
from csv_diff.formatter import format_diff
from csv_diff.filter import parse_columns, validate_columns, filter_rows, FilterError
from csv_diff.sorter import parse_sort_key, sort_diff, SortError
from csv_diff.stats import compute_stats, format_stats, has_changes
from csv_diff.pager import page_or_print
from csv_diff.truncate import parse_max_width, truncate_row, TruncateError
from csv_diff.context import parse_context_lines, add_context, ContextError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csv-diff",
        description="Compare two CSV files and show human-readable diffs.",
    )
    p.add_argument("old", help="Original CSV file")
    p.add_argument("new", help="Updated CSV file")
    p.add_argument("--key", default=None, help="Column to use as row identifier")
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default: comma)")
    p.add_argument("--columns", default=None, help="Comma-separated list of columns to compare")
    p.add_argument("--sort", default=None, choices=["key", "type"], help="Sort diff output")
    p.add_argument("--stats", action="store_true", help="Print summary statistics")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colour output")
    p.add_argument("--color", action="store_true", help="Force ANSI colour output")
    p.add_argument("--max-width", default=None, help="Truncate cell values to this width")
    p.add_argument("--context", default=None, help="Number of unchanged context rows to show around each change")
    p.add_argument("--pager", action="store_true", help="Page output through $PAGER")
    return p


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    parser = build_parser()
    args = parser.parse_args(argv)

    use_color = False if args.no_color else (True if args.color else None)

    try:
        max_width = parse_max_width(args.max_width)
    except TruncateError as exc:
        parser.error(str(exc))

    try:
        context_n = parse_context_lines(args.context)
    except ContextError as exc:
        parser.error(str(exc))

    try:
        old_rows, old_headers = read_csv(args.old, delimiter=args.delimiter)
        new_rows, new_headers = read_csv(args.new, delimiter=args.delimiter)
    except CSVReadError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        validate_matching_headers(old_headers, new_headers)
    except CSVReadError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        columns = parse_columns(args.columns)
        if columns:
            validate_columns(columns, old_headers)
    except FilterError as exc:
        parser.error(str(exc))

    key_col = get_key_column(args.key, old_headers)

    if max_width is not None:
        old_rows = [truncate_row(r, max_width) for r in old_rows]
        new_rows = [truncate_row(r, max_width) for r in new_rows]

    if columns:
        old_rows = filter_rows(old_rows, columns, key_col)
        new_rows = filter_rows(new_rows, columns, key_col)

    diff = diff_csv(old_rows, new_rows, key_col=key_col)

    try:
        sort_key = parse_sort_key(args.sort)
        if sort_key:
            diff = sort_diff(diff, sort_key=sort_key, key_col=key_col)
    except SortError as exc:
        parser.error(str(exc))

    output_events = diff
    if context_n is not None and context_n > 0:
        output_events = add_context(diff, old_rows, key_col=key_col, n=context_n)

    output = format_diff(output_events, use_color=bool(use_color))

    if args.stats:
        stats = compute_stats(diff)
        output = (output + "\n\n" + format_stats(stats)).strip()

    if output:
        page_or_print(output, force_pager=args.pager, use_color=bool(use_color))

    return 1 if has_changes(diff) else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
