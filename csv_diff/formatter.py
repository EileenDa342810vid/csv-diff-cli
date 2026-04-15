"""Human-readable formatting for CSV diff results."""

from __future__ import annotations

from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.truncate import truncate_row
from csv_diff.color import added as color_added, removed as color_removed, modified as color_modified


def _format_row(row: dict[str, str], prefix: str, color_fn=None) -> str:
    """Format a single row dict as a prefixed key=value line."""
    parts = ", ".join(f"{k}={v}" for k, v in row.items())
    line = f"{prefix} {parts}"
    if color_fn is not None:
        line = color_fn(line)
    return line


def format_diff(
    diff: list,
    *,
    color: bool = False,
    max_width: int | None = None,
) -> str:
    """Render a list of diff events as a human-readable string.

    Parameters
    ----------
    diff:
        List of :class:`RowAdded`, :class:`RowRemoved`, or
        :class:`RowModified` instances.
    color:
        When *True*, ANSI colour codes are applied.
    max_width:
        When given, cell values longer than this are truncated with an
        ellipsis before formatting.
    """
    if not diff:
        return "No differences found."

    lines: list[str] = []
    for event in diff:
        if isinstance(event, RowAdded):
            row = truncate_row(event.row, max_width)
            lines.append(_format_row(row, "+", color_fn=color_added if color else None))
        elif isinstance(event, RowRemoved):
            row = truncate_row(event.row, max_width)
            lines.append(_format_row(row, "-", color_fn=color_removed if color else None))
        elif isinstance(event, RowModified):
            before = truncate_row(event.before, max_width)
            after = truncate_row(event.after, max_width)
            lines.append(_format_row(before, "-", color_fn=color_removed if color else None))
            lines.append(_format_row(after, "+", color_fn=color_added if color else None))
    return "\n".join(lines)
