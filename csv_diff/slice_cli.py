"""CLI helpers for the --slice feature."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Sequence

from csv_diff.slice import SliceConfig, SliceError, describe_slice, parse_slice, slice_diff

DiffEvent = object  # keep import light; real type comes from diff module


def add_slice_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--slice",
        metavar="[START:]STOP",
        default=None,
        help="Only show a window of diff events, e.g. '10' or '5:20'.",
    )


def resolve_slice(args: argparse.Namespace) -> Optional[SliceConfig]:
    raw = getattr(args, "slice", None)
    if not raw:
        return None
    try:
        return parse_slice(raw)
    except (SliceError, ValueError) as exc:
        print(f"error: --slice: {exc}", file=sys.stderr)
        sys.exit(2)


def apply_slice(
    events: Sequence,
    cfg: Optional[SliceConfig],
    *,
    verbose: bool = False,
) -> List:
    result = slice_diff(events, cfg)
    if verbose and cfg is not None:
        print(describe_slice(cfg, len(events)))
    return result
