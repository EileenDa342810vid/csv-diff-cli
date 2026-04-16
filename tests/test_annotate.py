"""Tests for csv_diff.annotate."""

from __future__ import annotations

import pytest

from csv_diff.annotate import (
    AnnotatedEvent,
    AnnotateError,
    _build_line_index,
    annotate_diff,
    format_line_ref,
)
from csv_diff.diff import RowAdded, RowModified, RowRemoved

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROWS_A = [
    {"id": "1", "name": "Alice", "score": "10"},
    {"id": "2", "name": "Bob",   "score": "20"},
    {"id": "3", "name": "Carol", "score": "30"},
]

ROWS_B = [
    {"id": "1", "name": "Alice",  "score": "99"},  # modified
    {"id": "3", "name": "Carol",  "score": "30"},  # unchanged
    {"id": "4", "name": "Dave",   "score": "40"},  # added
]

# ---------------------------------------------------------------------------
# _build_line_index
# ---------------------------------------------------------------------------

def test_build_line_index_assigns_correct_lines():
    index = _build_line_index(ROWS_A, "id")
    assert index == {"1": 2, "2": 3, "3": 4}


def test_build_line_index_empty_rows():
    assert _build_line_index([], "id") == {}


def test_build_line_index_skips_duplicate_keys():
    rows = [
        {"id": "1", "val": "a"},
        {"id": "1", "val": "b"},
    ]
    index = _build_line_index(rows, "id")
    assert index["1"] == 2  # first occurrence wins

# ---------------------------------------------------------------------------
# annotate_diff
# ---------------------------------------------------------------------------

def _make_events():
    modified = RowModified(
        key="1",
        old={"id": "1", "name": "Alice", "score": "10"},
        new={"id": "1", "name": "Alice", "score": "99"},
    )
    removed = RowRemoved(key="2", row={"id": "2", "name": "Bob", "score": "20"})
    added   = RowAdded(key="4",  row={"id": "4", "name": "Dave", "score": "40"})
    return [modified, removed, added]


def test_annotate_diff_returns_correct_count():
    events = _make_events()
    result = annotate_diff(events, ROWS_A, ROWS_B, "id")
    assert len(result) == 3


def test_annotate_diff_modified_has_both_lines():
    events = _make_events()
    result = annotate_diff(events, ROWS_A, ROWS_B, "id")
    modified_ann = result[0]
    assert modified_ann.line_a == 2
    assert modified_ann.line_b == 2


def test_annotate_diff_removed_has_no_line_b():
    events = _make_events()
    result = annotate_diff(events, ROWS_A, ROWS_B, "id")
    removed_ann = result[1]
    assert removed_ann.line_a == 3
    assert removed_ann.line_b is None


def test_annotate_diff_added_has_no_line_a():
    events = _make_events()
    result = annotate_diff(events, ROWS_A, ROWS_B, "id")
    added_ann = result[2]
    assert added_ann.line_a is None
    assert added_ann.line_b == 3

# ---------------------------------------------------------------------------
# format_line_ref
# ---------------------------------------------------------------------------

def test_format_line_ref_both_present():
    event = RowModified(key="1", old={}, new={})
    ann = AnnotatedEvent(event, line_a=2, line_b=4)
    assert format_line_ref(ann) == "L2 -> L4"


def test_format_line_ref_added():
    event = RowAdded(key="5", row={})
    ann = AnnotatedEvent(event, line_a=None, line_b=6)
    assert format_line_ref(ann) == "(new) -> L6"


def test_format_line_ref_removed():
    event = RowRemoved(key="2", row={})
    ann = AnnotatedEvent(event, line_a=3, line_b=None)
    assert format_line_ref(ann) == "L3 -> (gone)"
