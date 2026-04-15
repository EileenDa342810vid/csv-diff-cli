"""CLI helpers that integrate the watch module with the argument parser."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

from csv_diff.watch import WatchError, parse_interval, watch


def add_watch_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --watch and --watch-interval flags on *parser*."""
    group = parser.add_argument_group("watch")
    group.add_argument(
        "--watch",
        action="store_true",
        default=False,
        help="Re-run the diff whenever either input file changes.",
    )
    group.add_argument(
        "--watch-interval",
        metavar="SECONDS",
        default=None,
        help="Polling interval in seconds when --watch is active (default: 2).",
    )


def maybe_watch(
    args: argparse.Namespace,
    path_a: Path,
    path_b: Path,
    callback: Callable[[], None],
) -> bool:
    """If ``args.watch`` is set, validate config and start the watch loop.

    Returns *True* if the watch loop was started (so the caller can skip its
    own single-run logic), *False* otherwise.

    Exits with code 2 on invalid configuration.
    """
    if not getattr(args, "watch", False):
        return False

    try:
        interval = parse_interval(getattr(args, "watch_interval", None))
    except WatchError as exc:
        print(f"csv-diff: watch error: {exc}", file=sys.stderr)
        sys.exit(2)

    try:
        watch(
            path_a=path_a,
            path_b=path_b,
            callback=callback,
            interval=interval,
        )
    except WatchError as exc:
        print(f"csv-diff: watch error: {exc}", file=sys.stderr)
        sys.exit(1)

    return True
