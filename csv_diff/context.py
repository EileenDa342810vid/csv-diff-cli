"""Context lines: include N unchanged rows surrounding each change."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved

DiffEvent = RowAdded | RowRemoved | RowModified


class ContextError(ValueError):
    """Raised when context configuration is invalid."""


@dataclass(frozen=True)
class ContextRow:
    """An unchanged row included for context around a diff event."""

    row: dict


def parse_context_lines(value: object) -> int | None:
    """Parse --context argument; return None when not supplied."""
    if value is None:
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ContextError(f"--context must be a non-negative integer, got: {value!r}")
    if n < 0:
        raise ContextError(f"--context must be >= 0, got: {n}")
    return n


def add_context(
    diff: Sequence[DiffEvent],
    all_rows: Sequence[dict],
    key_col: str,
    n: int,
) -> List[DiffEvent | ContextRow]:
    """Interleave *n* unchanged context rows around each changed row.

    *all_rows* is the ordered list of rows from the **old** file.  Rows that
    do not appear in *diff* at all are candidates for context lines.
    """
    if n == 0:
        return list(diff)

    changed_keys: set = set()
    for event in diff:
        if isinstance(event, RowAdded):
            changed_keys.add(event.row[key_col])
        elif isinstance(event, RowRemoved):
            changed_keys.add(event.row[key_col])
        elif isinstance(event, RowModified):
            changed_keys.add(event.old_row[key_col])

    unchanged = [r for r in all_rows if r[key_col] not in changed_keys]
    key_to_index = {r[key_col]: i for i, r in enumerate(unchanged)}

    context_keys: set = set()
    for event in diff:
        if isinstance(event, RowAdded):
            continue
        key = (
            event.row[key_col]
            if isinstance(event, RowRemoved)
            else event.old_row[key_col]
        )
        if key in key_to_index:
            idx = key_to_index[key]
            for neighbour in unchanged[max(0, idx - n) : idx + n + 1]:
                context_keys.add(neighbour[key_col])

    result: List[DiffEvent | ContextRow] = []
    diff_keys_ordered = [
        (e.row[key_col] if isinstance(e, (RowAdded, RowRemoved)) else e.old_row[key_col])
        for e in diff
    ]
    inserted: set = set()

    for event in diff:
        result.append(event)

    context_rows = [ContextRow(row=r) for r in unchanged if r[key_col] in context_keys]
    result.extend(context_rows)
    return result
