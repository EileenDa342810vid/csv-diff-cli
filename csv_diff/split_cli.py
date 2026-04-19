"""CLI helpers for the --split flag."""
from __future__ import annotations
import argparse
from csv_diff.split import split_diff, format_split


def add_split_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--split",
        action="store_true",
        default=False,
        help="Print a summary table with counts split by change type.",
    )


def maybe_print_split(args: argparse.Namespace, events: list) -> bool:
    """If --split is set, print the split summary and return True."""
    if not getattr(args, "split", False):
        return False
    result = split_diff(events)
    print(format_split(result))
    return True
