"""Detect and report duplicate key rows within a CSV dataset."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DedupeError(Exception):
    """Raised when deduplication validation fails."""


@dataclass
class DuplicateGroup:
    key: str
    rows: List[Dict[str, str]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.rows)


def find_duplicates(
    rows: List[Dict[str, str]],
    key_column: str,
) -> List[DuplicateGroup]:
    """Return groups of rows that share the same key value."""
    seen: Dict[str, DuplicateGroup] = {}
    for row in rows:
        key = row.get(key_column)
        if key is None:
            raise DedupeError(f"Row missing key column '{key_column}': {row}")
        if key not in seen:
            seen[key] = DuplicateGroup(key=key)
        seen[key].rows.append(row)
    return [g for g in seen.values() if g.count > 1]


def format_duplicates(
    groups: List[DuplicateGroup],
    key_column: str,
    label: str = "file",
) -> Optional[str]:
    """Return a human-readable report of duplicate groups, or None if clean."""
    if not groups:
        return None
    lines = [f"Duplicates found in {label} (key: {key_column})"]
    for g in groups:
        lines.append(f"  '{g.key}' appears {g.count} times")
        for i, row in enumerate(g.rows, 1):
            lines.append(f"    [{i}] {row}")
    return "\n".join(lines)


def assert_no_duplicates(
    rows: List[Dict[str, str]],
    key_column: str,
    label: str = "file",
) -> None:
    """Raise DedupeError if any duplicate keys are found."""
    groups = find_duplicates(rows, key_column)
    if groups:
        report = format_duplicates(groups, key_column, label)
        raise DedupeError(report)
