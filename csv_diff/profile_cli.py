"""CLI helpers for the --profile feature."""
from __future__ import annotations

from typing import List

from csv_diff.profile import profile_diff, format_profile


def add_profile_arguments(parser) -> None:
    """Attach --profile flag to an argparse parser."""
    parser.add_argument(
        "--profile",
        action="store_true",
        default=False,
        help="Print a per-column change profile after the diff.",
    )


def maybe_print_profile(args, events: list, headers: List[str]) -> None:
    """If --profile was requested, compute and print the profile."""
    if not getattr(args, "profile", False):
        return

    prof = profile_diff(events, headers)
    print("\n--- Column Profile ---")
    print(format_profile(prof))
