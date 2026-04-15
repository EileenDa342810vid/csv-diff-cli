"""Generate and apply patch-style output for CSV diffs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class PatchError(Exception):
    """Raised when patch generation or parsing fails."""


@dataclass
class PatchHunk:
    """A single hunk in a unified-style patch."""

    key: str
    change_type: str  # 'added', 'removed', 'modified'
    lines: List[str]


def _row_to_lines(row: dict, prefix: str) -> List[str]:
    """Format a row's fields as prefixed patch lines."""
    return [f"{prefix}{col}: {val}" for col, val in row.items()]


def parse_patch_format(value: Optional[str]) -> Optional[str]:
    """Validate and normalise a patch format string.

    Accepts 'unified' or None.  Raises PatchError on unknown values.
    """
    if value is None:
        return None
    normalised = value.strip().lower()
    if normalised not in {"unified"}:
        raise PatchError(
            f"Unknown patch format {value!r}. Supported formats: unified"
        )
    return normalised


def build_hunks(diff: list) -> List[PatchHunk]:
    """Convert a list of diff events into PatchHunk objects."""
    hunks: List[PatchHunk] = []
    for event in diff:
        if isinstance(event, RowAdded):
            lines = _row_to_lines(event.row, "+ ")
            hunks.append(PatchHunk(key=str(event.key), change_type="added", lines=lines))
        elif isinstance(event, RowRemoved):
            lines = _row_to_lines(event.row, "- ")
            hunks.append(PatchHunk(key=str(event.key), change_type="removed", lines=lines))
        elif isinstance(event, RowModified):
            lines = _row_to_lines(event.old_row, "- ") + _row_to_lines(event.new_row, "+ ")
            hunks.append(PatchHunk(key=str(event.key), change_type="modified", lines=lines))
    return hunks


def format_patch(hunks: List[PatchHunk]) -> str:
    """Render PatchHunk objects as a unified-style patch string."""
    if not hunks:
        return ""
    parts: List[str] = []
    for hunk in hunks:
        header = f"@@ {hunk.change_type} key={hunk.key} @@"
        parts.append(header)
        parts.extend(hunk.lines)
        parts.append("")
    return "\n".join(parts).rstrip("\n")
