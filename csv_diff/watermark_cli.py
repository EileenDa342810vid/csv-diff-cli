"""CLI helpers for the --watermark feature."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from csv_diff.watermark import (
    WatermarkError,
    check_watermark,
    format_watermark,
    parse_watermark_path,
)


def add_watermark_arguments(parser: argparse.ArgumentParser) -> None:
    """Register watermark-related flags on *parser*."""
    parser.add_argument(
        "--watermark",
        metavar="FILE",
        default=None,
        help="Path to a JSON file that tracks the high-water-mark change count.",
    )
    parser.add_argument(
        "--watermark-fail-on-high",
        action="store_true",
        default=False,
        help="Exit with code 3 when a new high-water-mark is reached.",
    )


def maybe_report_watermark(
    args: argparse.Namespace,
    total_changes: int,
    *,
    file=sys.stdout,
) -> Optional[bool]:
    """Check and optionally print the watermark. Return True when printed."""
    path = parse_watermark_path(getattr(args, "watermark", None))
    if path is None:
        return None
    try:
        wm = check_watermark(path, total_changes)
    except WatermarkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    print(format_watermark(wm), file=file)
    if getattr(args, "watermark_fail_on_high", False) and wm.is_new_high:
        sys.exit(3)
    return True
