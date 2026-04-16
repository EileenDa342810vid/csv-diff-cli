"""Column renaming support for csv-diff-cli."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


class RenameError(Exception):
    """Raised when column rename configuration is invalid."""


@dataclass
class ColumnRename:
    mapping: Dict[str, str]  # old_name -> new_name


def parse_renames(value: Optional[str]) -> Optional[ColumnRename]:
    """Parse a comma-separated list of old=new rename pairs."""
    if not value or not value.strip():
        return None
    mapping: Dict[str, str] = {}
    for part in value.split(","):
        part = part.strip()
        if "=" not in part:
            raise RenameError(f"Invalid rename spec (expected old=new): {part!r}")
        old, new = part.split("=", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise RenameError(f"Rename spec has empty name: {part!r}")
        mapping[old] = new
    return ColumnRename(mapping=mapping)


def validate_renames(rename: ColumnRename, headers: List[str]) -> None:
    """Raise RenameError if any source column is not present in headers."""
    for old in rename.mapping:
        if old not in headers:
            raise RenameError(
                f"Rename source column {old!r} not found in headers: {headers}"
            )


def apply_renames(rename: ColumnRename, headers: List[str]) -> List[str]:
    """Return a new header list with columns renamed."""
    return [rename.mapping.get(h, h) for h in headers]


def rename_rows(
    rename: ColumnRename, rows: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Return rows with keys renamed according to the mapping."""
    result = []
    for row in rows:
        new_row = {rename.mapping.get(k, k): v for k, v in row.items()}
        result.append(new_row)
    return result
