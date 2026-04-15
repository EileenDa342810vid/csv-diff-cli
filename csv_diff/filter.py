"""Column filtering and selection utilities for CSV diff output."""

from typing import Optional


class FilterError(Exception):
    """Raised when a filter configuration is invalid."""


def parse_columns(columns_arg: Optional[str]) -> Optional[list[str]]:
    """Parse a comma-separated list of column names into a list.

    Args:
        columns_arg: Comma-separated column names, or None.

    Returns:
        List of stripped column names, or None if input is None.
    """
    if columns_arg is None:
        return None
    parts = [c.strip() for c in columns_arg.split(",")]
    if not all(parts):
        raise FilterError("Column list contains empty entries.")
    return parts


def validate_columns(requested: list[str], available: list[str]) -> None:
    """Ensure all requested columns exist in the available headers.

    Args:
        requested: Column names the user wants to filter to.
        available: Column names present in the CSV file.

    Raises:
        FilterError: If any requested column is not in available.
    """
    missing = [c for c in requested if c not in available]
    if missing:
        raise FilterError(
            f"Unknown column(s): {', '.join(missing)}. "
            f"Available: {', '.join(available)}"
        )


def filter_row(row: dict, columns: Optional[list[str]]) -> dict:
    """Return a copy of *row* containing only the selected columns.

    If *columns* is None all fields are kept.

    Args:
        row: Original row dictionary.
        columns: Columns to keep, or None for all.

    Returns:
        Filtered row dictionary.
    """
    if columns is None:
        return dict(row)
    return {k: v for k, v in row.items() if k in columns}


def filter_rows(rows: list[dict], columns: Optional[list[str]]) -> list[dict]:
    """Apply :func:`filter_row` to every row in *rows*."""
    return [filter_row(r, columns) for r in rows]
