"""Sorting utilities for CSV diff output."""

from __future__ import annotations

from typing import List, Optional

from csv_diff.diff import RowAdded, RowRemoved, RowModified


class SortError(Exception):
    """Raised when an invalid sort key is specified."""


_SORT_KEYS = ("key", "type", "column")


def parse_sort_key(value: Optional[str]) -> Optional[str]:
    """Validate and normalise a sort-key string from the CLI.

    Returns None if *value* is None, otherwise returns the lower-cased key.
    Raises SortError for unrecognised values.
    """
    if value is None:
        return None
    normalised = value.strip().lower()
    if normalised not in _SORT_KEYS:
        raise SortError(
            f"Unknown sort key {value!r}. Choose from: {', '.join(_SORT_KEYS)}"
        )
    return normalised


def _change_type_order(change) -> int:
    """Return a numeric priority for ordering change types.

    Order: added (0) → removed (1) → modified (2) → unknown (3).
    """
    if isinstance(change, RowAdded):
        return 0
    if isinstance(change, RowRemoved):
        return 1
    if isinstance(change, RowModified):
        return 2
    return 3


def _first_changed_column(change: RowModified) -> str:
    """Return the lexicographically first column name that differs in *change*.

    Returns an empty string if ``change.diffs`` is empty, so that such rows
    sort before rows with no diff information at all.
    """
    if change.diffs:
        return sorted(change.diffs.keys())[0]
    return ""


def sort_diff(changes: List, sort_key: Optional[str]) -> List:
    """Return a new list of *changes* sorted according to *sort_key*.

    sort_key values:
      ``"key"``    – sort by the row key value (alphabetical)
      ``"type"``   – group by change type (added, removed, modified)
      ``"column"`` – sort modified rows by the first changed column name;
                     added/removed rows come last, ordered by key
      ``None``     – return original order
    """
    if sort_key is None:
        return list(changes)

    if sort_key == "key":
        return sorted(changes, key=lambda c: str(c.key))

    if sort_key == "type":
        return sorted(changes, key=lambda c: (_change_type_order(c), str(c.key)))

    if sort_key == "column":
        def _col_sort(change):
            if isinstance(change, RowModified):
                return (0, _first_changed_column(change), str(change.key))
            return (1, "", str(change.key))

        return sorted(changes, key=_col_sort)

    # Should not reach here if parse_sort_key was called first.
    return list(changes)
