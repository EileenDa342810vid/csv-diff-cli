"""Annotate diff output with line numbers from the original CSV files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .diff import RowAdded, RowModified, RowRemoved


class AnnotateError(Exception):
    """Raised when annotation cannot be applied."""


@dataclass(frozen=True)
class AnnotatedEvent:
    """A diff event decorated with source line numbers."""

    event: RowAdded | RowRemoved | RowModified
    line_a: Optional[int]  # 1-based line in file A (None for pure additions)
    line_b: Optional[int]  # 1-based line in file B (None for pure removals)


def _build_line_index(rows: List[Dict[str, str]], key_column: str) -> Dict[str, int]:
    """Return a mapping of key-value -> 1-based data line number (header = line 1)."""
    index: Dict[str, int] = {}
    for position, row in enumerate(rows, start=2):  # line 1 is the header
        key = row.get(key_column, "")
        if key not in index:
            index[key] = position
    return index


def annotate_diff(
    events: List[RowAdded | RowRemoved | RowModified],
    rows_a: List[Dict[str, str]],
    rows_b: List[Dict[str, str]],
    key_column: str,
) -> List[AnnotatedEvent]:
    """Attach line numbers from the original files to each diff event.

    Parameters
    ----------
    events:      list of diff events produced by :func:`csv_diff.diff.diff_csv`.
    rows_a:      parsed rows from the first ("old") CSV file.
    rows_b:      parsed rows from the second ("new") CSV file.
    key_column:  the column used as the unique row identifier.

    Returns
    -------
    A list of :class:`AnnotatedEvent` objects in the same order as *events*.
    """
    index_a = _build_line_index(rows_a, key_column)
    index_b = _build_line_index(rows_b, key_column)

    annotated: List[AnnotatedEvent] = []
    for event in events:
        key = event.key
        if isinstance(event, RowAdded):
            annotated.append(AnnotatedEvent(event, line_a=None, line_b=index_b.get(key)))
        elif isinstance(event, RowRemoved):
            annotated.append(AnnotatedEvent(event, line_a=index_a.get(key), line_b=None))
        elif isinstance(event, RowModified):
            annotated.append(
                AnnotatedEvent(event, line_a=index_a.get(key), line_b=index_b.get(key))
            )
        else:
            raise AnnotateError(f"Unknown event type: {type(event)}")
    return annotated


def format_line_ref(annotated: AnnotatedEvent) -> str:
    """Return a short human-readable line-reference string, e.g. ``'L4 -> L5'``."""
    a = f"L{annotated.line_a}" if annotated.line_a is not None else "(new)"
    b = f"L{annotated.line_b}" if annotated.line_b is not None else "(gone)"
    return f"{a} -> {b}"
