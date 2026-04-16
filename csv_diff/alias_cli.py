"""CLI integration for column aliasing."""

from __future__ import annotations

import argparse
from typing import List, Optional

from csv_diff.alias import AliasError, ColumnAlias, parse_aliases, validate_aliases


def add_alias_arguments(parser: argparse.ArgumentParser) -> None:
    """Add --alias argument to an existing ArgumentParser."""
    parser.add_argument(
        "--alias",
        metavar="ORIG:NAME,...",
        default=None,
        help=(
            "Rename columns in output. Comma-separated list of original:display pairs. "
            "Example: --alias name:full_name,dob:date_of_birth"
        ),
    )


def resolve_aliases(
    raw: Optional[str], headers: List[str]
) -> Optional[ColumnAlias]:
    """Parse and validate aliases against known headers.

    Returns a ColumnAlias or None. Raises SystemExit on error.
    """
    try:
        alias = parse_aliases(raw)
        if alias is not None:
            validate_aliases(alias, headers)
        return alias
    except AliasError as exc:
        import sys
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
