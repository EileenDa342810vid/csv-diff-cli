"""Limit the number of diff events shown."""
from __future__ import annotations

from typing import List, Optional, Union

from csv_diff.diff import RowAdded, RowModified, RowRemoved

DiffEvent = Union[RowAdded, RowRemoved, RowModified]


class LimitError(ValueError):
    """Raised when an invalid limit value is supplied."""


def parse_limit(value: Optional[Union[int, str]]) -> Optional[int]:
    """Return an integer limit or None (no limit).

    Args:
        value: Raw value from CLI or config; None means unlimited.

    Returns:
        Parsed integer, or None.

    Raises:
        LimitError: If *value* cannot be converted or is not positive.
    """
    if value is None:
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise LimitError(f"--limit must be an integer, got {value!r}")
    if n <= 0:
        raise LimitError(f"--limit must be a positive integer, got {n}")
    return n


def limit_diff(events: List[DiffEvent], n: Optional[int]) -> List[DiffEvent]:
    """Return at most *n* events from *events*.

    Args:
        events: Full list of diff events.
        n:      Maximum number of events to return; None returns all.

    Returns:
        Possibly-truncated list of events.
    """
    if n is None:
        return events
    return events[:n]


def was_truncated(events: List[DiffEvent], n: Optional[int]) -> bool:
    """Return True when *events* would be cut by *limit_diff*."""
    if n is None:
        return False
    return len(events) > n
