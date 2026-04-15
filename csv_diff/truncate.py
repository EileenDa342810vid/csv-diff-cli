"""Truncation helpers for long cell values in diff output."""

from __future__ import annotations

DEFAULT_MAX_WIDTH = 40
_ELLIPSIS = "..."


class TruncateError(ValueError):
    """Raised when truncation parameters are invalid."""


def parse_max_width(value: str | int | None) -> int | None:
    """Parse a max-width value from a CLI string or integer.

    Returns None when *value* is None (meaning: no truncation).
    Raises TruncateError for non-positive integers.
    """
    if value is None:
        return None
    try:
        width = int(value)
    except (TypeError, ValueError) as exc:
        raise TruncateError(f"max-width must be an integer, got {value!r}") from exc
    if width <= 0:
        raise TruncateError(f"max-width must be a positive integer, got {width}")
    return width


def truncate_value(text: str, max_width: int | None) -> str:
    """Truncate *text* to *max_width* characters, appending an ellipsis.

    If *max_width* is None the original text is returned unchanged.
    The returned string is always at most *max_width* characters long.
    """
    if max_width is None:
        return text
    if len(text) <= max_width:
        return text
    # Ensure the ellipsis fits within the budget.
    cut = max(0, max_width - len(_ELLIPSIS))
    return text[:cut] + _ELLIPSIS


def truncate_row(row: dict[str, str], max_width: int | None) -> dict[str, str]:
    """Return a copy of *row* with every value truncated to *max_width*."""
    if max_width is None:
        return row
    return {col: truncate_value(val, max_width) for col, val in row.items()}
