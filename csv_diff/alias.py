"""Column aliasing: rename columns in diff output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


class AliasError(Exception):
    pass


@dataclass
class ColumnAlias:
    mapping: Dict[str, str]  # original -> display name


def parse_aliases(raw: Optional[str]) -> Optional[ColumnAlias]:
    """Parse 'orig:alias,orig2:alias2' into a ColumnAlias."""
    if not raw:
        return None
    mapping: Dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if ":" not in entry:
            raise AliasError(
                f"Invalid alias entry {entry!r}: expected 'original:alias' format."
            )
        orig, _, alias = entry.partition(":")
        orig, alias = orig.strip(), alias.strip()
        if not orig or not alias:
            raise AliasError(
                f"Invalid alias entry {entry!r}: both original and alias must be non-empty."
            )
        mapping[orig] = alias
    return ColumnAlias(mapping=mapping)


def validate_aliases(alias: ColumnAlias, headers: List[str]) -> None:
    """Raise AliasError if any aliased column is not present in headers."""
    missing = [col for col in alias.mapping if col not in headers]
    if missing:
        raise AliasError(
            f"Aliased column(s) not found in CSV headers: {', '.join(missing)}"
        )


def apply_aliases(row: Dict[str, str], alias: Optional[ColumnAlias]) -> Dict[str, str]:
    """Return a new row dict with column keys renamed per alias mapping."""
    if alias is None:
        return row
    return {alias.mapping.get(k, k): v for k, v in row.items()}


def rename_headers(headers: List[str], alias: Optional[ColumnAlias]) -> List[str]:
    """Return headers with aliases applied."""
    if alias is None:
        return headers
    return [alias.mapping.get(h, h) for h in headers]
