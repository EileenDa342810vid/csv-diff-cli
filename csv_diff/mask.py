"""Mask rows in a diff based on a regex pattern applied to a column value."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved

DiffEvent = RowAdded | RowRemoved | RowModified


class MaskError(ValueError):
    pass


@dataclass(frozen=True)
class MaskRule:
    column: str
    pattern: re.Pattern


def parse_mask_rule(spec: Optional[str]) -> Optional[MaskRule]:
    """Parse a mask spec of the form 'column=pattern'."""
    if not spec:
        return None
    if "=" not in spec:
        raise MaskError(f"Mask spec must be 'column=pattern', got: {spec!r}")
    column, _, pattern = spec.partition("=")
    column = column.strip()
    pattern = pattern.strip()
    if not column:
        raise MaskError("Mask column name must not be empty.")
    if not pattern:
        raise MaskError("Mask pattern must not be empty.")
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        raise MaskError(f"Invalid regex pattern {pattern!r}: {exc}") from exc
    return MaskRule(column=column, pattern=compiled)


def _row_value(event: DiffEvent, column: str) -> Optional[str]:
    if isinstance(event, RowAdded):
        return event.row.get(column)
    if isinstance(event, RowRemoved):
        return event.row.get(column)
    if isinstance(event, RowModified):
        return event.new_row.get(column)
    return None


def apply_mask(events: Sequence[DiffEvent], rule: Optional[MaskRule]) -> List[DiffEvent]:
    """Return only events where the column value matches the pattern."""
    if rule is None:
        return list(events)
    return [
        e for e in events
        if (val := _row_value(e, rule.column)) is not None
        and rule.pattern.search(val)
    ]
