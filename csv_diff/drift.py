"""Detect schema drift between two CSV file headers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence


class DriftError(Exception):
    """Raised when drift detection fails."""


@dataclass
class SchemaDrift:
    added_columns: List[str] = field(default_factory=list)
    removed_columns: List[str] = field(default_factory=list)
    reordered: bool = False

    @property
    def has_drift(self) -> bool:
        return bool(self.added_columns or self.removed_columns or self.reordered)


def detect_drift(old_headers: Sequence[str], new_headers: Sequence[str]) -> SchemaDrift:
    """Compare two header sequences and return a SchemaDrift summary."""
    old_set = set(old_headers)
    new_set = set(new_headers)

    added = [c for c in new_headers if c not in old_set]
    removed = [c for c in old_headers if c not in new_set]

    common_old = [c for c in old_headers if c in new_set]
    common_new = [c for c in new_headers if c in old_set]
    reordered = common_old != common_new

    return SchemaDrift(added_columns=added, removed_columns=removed, reordered=reordered)


def format_drift(drift: SchemaDrift) -> Optional[str]:
    """Return a human-readable drift report, or None if no drift."""
    if not drift.has_drift:
        return None

    lines = ["Schema drift detected:"]
    if drift.added_columns:
        lines.append("  Added columns   : " + ", ".join(drift.added_columns))
    if drift.removed_columns:
        lines.append("  Removed columns : " + ", ".join(drift.removed_columns))
    if drift.reordered:
        lines.append("  Column order changed")
    return "\n".join(lines)
