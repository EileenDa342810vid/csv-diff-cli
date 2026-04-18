"""CLI integration for schema drift detection."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .drift import detect_drift, format_drift


def add_drift_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--drift",
        action="store_true",
        default=False,
        help="Report schema drift (added/removed/reordered columns) and exit non-zero if drift found.",
    )


def maybe_report_drift(
    args: argparse.Namespace,
    old_headers: List[str],
    new_headers: List[str],
) -> bool:
    """Print drift report if --drift flag is set.

    Returns True if drift was reported (caller may choose to exit).
    """
    if not getattr(args, "drift", False):
        return False

    drift = detect_drift(old_headers, new_headers)
    report = format_drift(drift)
    if report:
        print(report)
        sys.exit(1)
    else:
        print("No schema drift detected.")
        sys.exit(0)
