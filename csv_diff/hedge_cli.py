"""CLI integration for the hedge (threshold-crossing) feature."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Sequence

from .hedge import (
    HedgeError,
    HedgeHit,
    HedgeRule,
    find_hedge_hits,
    format_hedge_hits,
    parse_hedge_rules,
    validate_hedge_columns,
)


def add_hedge_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --hedge flag on *parser*."""
    parser.add_argument(
        "--hedge",
        metavar="COL:THRESHOLD[,...]",
        default=None,
        help=(
            "Report rows where a numeric column crosses the given threshold. "
            "Example: --hedge price:100,qty:0"
        ),
    )
    parser.add_argument(
        "--hedge-only",
        action="store_true",
        default=False,
        help="Exit with code 4 if any hedge threshold crossings are found.",
    )


def resolve_hedge(
    args: argparse.Namespace, headers: Sequence[str]
) -> Optional[List[HedgeRule]]:
    """Parse and validate hedge rules from CLI args."""
    spec: Optional[str] = getattr(args, "hedge", None)
    try:
        rules = parse_hedge_rules(spec)
        if rules:
            validate_hedge_columns(rules, headers)
        return rules
    except HedgeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)


def maybe_print_hedge(
    args: argparse.Namespace,
    rules: Optional[List[HedgeRule]],
    events: Sequence,
) -> bool:
    """Print hedge report if rules are configured.  Return True if printed."""
    if not rules:
        return False
    hits: List[HedgeHit] = find_hedge_hits(events, rules)
    print(format_hedge_hits(hits))
    if getattr(args, "hedge_only", False) and hits:
        sys.exit(4)
    return True
