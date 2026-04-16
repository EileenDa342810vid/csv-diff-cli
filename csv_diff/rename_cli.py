"""CLI integration for column renaming."""

from __future__ import annotations

import argparse
from typing import List, Optional, Tuple

from csv_diff.rename import (
    ColumnRename,
    RenameError,
    apply_renames,
    parse_renames,
    rename_rows,
    validate_renames,
)


def add_rename_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --rename flag on *parser*."""
    parser.add_argument(
        "--rename",
        metavar="OLD=NEW,...",
        default=None,
        help=(
            "Rename columns before diffing. "
            "Comma-separated list of old=new pairs, e.g. 'id=ID,name=Name'."
        ),
    )


def resolve_renames(
    args: argparse.Namespace,
    headers: List[str],
) -> Tuple[Optional[ColumnRename], List[str]]:
    """Parse and validate renames; return (rename_obj, new_headers).

    Calls sys.exit(2) on error so it integrates cleanly with the CLI.
    """
    import sys

    raw = getattr(args, "rename", None)
    try:
        rename = parse_renames(raw)
    except RenameError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    if rename is None:
        return None, headers

    try:
        validate_renames(rename, headers)
    except RenameError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    new_headers = apply_renames(rename, headers)
    return rename, new_headers
