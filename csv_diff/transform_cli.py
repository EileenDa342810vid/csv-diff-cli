"""CLI helpers for the --transform flag."""

from __future__ import annotations

import argparse
from typing import List, Optional

from csv_diff.transform import TransformError, parse_transforms, validate_transforms


def add_transform_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--transform",
        metavar="COL:FN,...",
        default=None,
        help=(
            "Apply a named transform to one or more columns before comparing. "
            "Format: 'column:transform[,column:transform]'. "
            "Available transforms: upper, lower, strip, title."
        ),
    )


def resolve_transforms(args: argparse.Namespace, headers: List[str]) -> Optional[dict]:
    """Parse and validate --transform from parsed args; exit on error."""
    raw: Optional[str] = getattr(args, "transform", None)
    try:
        transforms = parse_transforms(raw)
        if transforms:
            validate_transforms(transforms, headers)
        return transforms
    except TransformError as exc:
        import sys
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
