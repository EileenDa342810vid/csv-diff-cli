"""Export diff results to alternative formats (JSON, Markdown)."""
from __future__ import annotations

import json
from typing import List

from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.stats import DiffStats


class ExportError(ValueError):
    """Raised when an unsupported export format is requested."""


SUPPORTED_FORMATS = ("json", "markdown")


def parse_export_format(value: str | None) -> str | None:
    """Validate and normalise an export format string."""
    if value is None:
        return None
    normalised = value.strip().lower()
    if normalised not in SUPPORTED_FORMATS:
        raise ExportError(
            f"Unknown export format {value!r}. "
            f"Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    return normalised


def _diff_to_dict(change) -> dict:
    if isinstance(change, RowAdded):
        return {"type": "added", "row": change.row}
    if isinstance(change, RowRemoved):
        return {"type": "removed", "row": change.row}
    if isinstance(change, RowModified):
        return {"type": "modified", "key": change.key, "before": change.before, "after": change.after}
    raise ExportError(f"Unknown change type: {type(change)}")


def export_json(changes: list, stats: DiffStats | None = None) -> str:
    """Serialise *changes* (and optional *stats*) to a JSON string."""
    payload: dict = {"changes": [_diff_to_dict(c) for c in changes]}
    if stats is not None:
        payload["stats"] = {
            "added": stats.added,
            "removed": stats.removed,
            "modified": stats.modified,
            "unchanged": stats.unchanged,
        }
    return json.dumps(payload, indent=2)


def _md_row(cells: List[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def export_markdown(changes: list) -> str:
    """Render *changes* as a Markdown table."""
    if not changes:
        return "_No differences found._"

    lines = []
    lines.append(_md_row(["Type", "Key / Details"]))
    lines.append(_md_row(["---", "---"]))
    for change in changes:
        if isinstance(change, RowAdded):
            detail = ", ".join(f"{k}={v}" for k, v in change.row.items())
            lines.append(_md_row(["➕ Added", detail]))
        elif isinstance(change, RowRemoved):
            detail = ", ".join(f"{k}={v}" for k, v in change.row.items())
            lines.append(_md_row(["➖ Removed", detail]))
        elif isinstance(change, RowModified):
            fields = ", ".join(
                f"{k}: {change.before.get(k)!r} → {change.after.get(k)!r}"
                for k in change.after
                if change.before.get(k) != change.after.get(k)
            )
            lines.append(_md_row(["✏️ Modified", f"{change.key}: {fields}"]))
    return "\n".join(lines)


def export_diff(changes: list, fmt: str, stats: DiffStats | None = None) -> str:
    """Dispatch to the correct exporter for *fmt*."""
    if fmt == "json":
        return export_json(changes, stats)
    if fmt == "markdown":
        return export_markdown(changes)
    raise ExportError(f"Unsupported format: {fmt!r}")
