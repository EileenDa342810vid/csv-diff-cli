"""Field-level diff highlighting for modified rows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from csv_diff.color import added, removed


class HighlightError(ValueError):
    """Raised when highlighting cannot be applied."""


@dataclass
class FieldDiff:
    """Represents a single changed field between two rows."""

    column: str
    old_value: str
    new_value: str


def diff_fields(
    old_row: Dict[str, str],
    new_row: Dict[str, str],
) -> List[FieldDiff]:
    """Return a list of FieldDiff for every column whose value changed.

    Args:
        old_row: The original row as a dict mapping column -> value.
        new_row: The updated row as a dict mapping column -> value.

    Returns:
        Ordered list of FieldDiff objects (one per changed column).

    Raises:
        HighlightError: If the two rows have different column sets.
    """
    if old_row.keys() != new_row.keys():
        raise HighlightError(
            "Cannot diff rows with different columns: "
            f"{set(old_row.keys())} vs {set(new_row.keys())}"
        )

    return [
        FieldDiff(column=col, old_value=old_row[col], new_value=new_row[col])
        for col in old_row
        if old_row[col] != new_row[col]
    ]


def format_field_diff(
    field: FieldDiff,
    *,
    use_color: bool = False,
) -> str:
    """Format a single FieldDiff as a human-readable string.

    Example output (no color)::

        age: 30 -> 31

    Args:
        field: The FieldDiff to format.
        use_color: When True, wrap old value in red and new value in green.

    Returns:
        Formatted string describing the change.
    """
    old = removed(field.old_value, force=use_color)
    new = added(field.new_value, force=use_color)
    return f"  {field.column}: {old} -> {new}"


def format_all_field_diffs(
    old_row: Dict[str, str],
    new_row: Dict[str, str],
    *,
    use_color: bool = False,
) -> List[str]:
    """Return formatted lines for every changed field between two rows.

    Args:
        old_row: The original row.
        new_row: The updated row.
        use_color: Enable ANSI colour output.

    Returns:
        List of formatted diff lines (empty list when rows are identical).
    """
    fields = diff_fields(old_row, new_row)
    return [format_field_diff(f, use_color=use_color) for f in fields]
