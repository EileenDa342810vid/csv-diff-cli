"""CLI integration for --threshold flag."""
from __future__ import annotations
import argparse
from typing import Optional
from csv_diff.threshold import parse_threshold, exceeds_threshold, describe_threshold, ThresholdConfig, ThresholdError
from csv_diff.stats import DiffStats


def add_threshold_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--threshold",
        metavar="N",
        default=None,
        help="Suppress output and exit 0 when total changes are below N.",
    )


def apply_threshold(
    args: argparse.Namespace,
    stats: DiffStats,
    output: str,
) -> tuple[str, int]:
    """Return (output_text, exit_code) after applying threshold logic."""
    try:
        config = parse_threshold(args.threshold)
    except ThresholdError as exc:
        return str(exc), 2

    if config is None:
        from csv_diff.stats import has_changes
        return output, 1 if has_changes(stats) else 0

    if exceeds_threshold(stats, config):
        from csv_diff.stats import has_changes
        return output, 1 if has_changes(stats) else 0
    else:
        return describe_threshold(config, stats), 0
