"""CLI integration for column tolerance comparison."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from csv_diff.compare import (
    CompareError,
    ToleranceConfig,
    build_tolerance_map,
    parse_tolerance_specs,
    validate_tolerance_columns,
)


def add_compare_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--tolerance",
        metavar="COL:VAL",
        help="Treat numeric differences within tolerance as equal. Format: col:0.01,col2:5",
        default=None,
    )


def resolve_tolerance(
    args: argparse.Namespace,
    headers: list[str],
) -> dict[str, float]:
    """Parse and validate --tolerance; return a tolerance map."""
    raw: Optional[str] = getattr(args, "tolerance", None)
    if not raw:
        return {}
    try:
        configs = parse_tolerance_specs(raw)
        if configs:
            validate_tolerance_columns(configs, headers)
        return build_tolerance_map(configs)
    except CompareError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
