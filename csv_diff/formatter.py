"""Human-readable formatting for diff events, including context rows."""
from __future__ import annotations

from typing import Iterable, List

from csv_diff.color import added, removed, modified, header
from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.highlight import format_all_field_diffs

try:
    from csv_diff.context import ContextRow
    _CONTEXT_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CONTEXT_AVAILABLE = False
    ContextRow = None  # type: ignore[assignment,misc]


def _format_row(label: str, row: dict, colour_fn=None) -> str:
    parts = [f"{label}"]
    for k, v in row.items():
        cell = f"  {k}: {v}"
        parts.append(colour_fn(cell) if colour_fn else cell)
    return "\n".join(parts)


def _format_context_row(row: dict) -> str:
    parts = ["  (context)"]
    for k, v in row.items():
        parts.append(f"    {k}: {v}")
    return "\n".join(parts)


def format_diff(
    diff: Iterable,
    *,
    use_color: bool = False,
    highlight: bool = True,
) -> str:
    lines: List[str] = []
    for event in diff:
        if _CONTEXT_AVAILABLE and isinstance(event, ContextRow):
            lines.append(_format_context_row(event.row))
            lines.append("")
            continue

        if isinstance(event, RowAdded):
            title = added("+ ROW ADDED", force=use_color)
            lines.append(_format_row(title, event.row, added if use_color else None))

        elif isinstance(event, RowRemoved):
            title = removed("- ROW REMOVED", force=use_color)
            lines.append(_format_row(title, event.row, removed if use_color else None))

        elif isinstance(event, RowModified):
            title = modified("~ ROW MODIFIED", force=use_color)
            lines.append(title)
            if highlight:
                field_lines = format_all_field_diffs(
                    event.old_row,
                    event.new_row,
                    use_color=use_color,
                )
                lines.extend(field_lines)
            else:
                lines.append(_format_row("  OLD", event.old_row))
                lines.append(_format_row("  NEW", event.new_row))

        lines.append("")
    return "\n".join(lines).rstrip()
