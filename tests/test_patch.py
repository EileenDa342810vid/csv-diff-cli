"""Tests for csv_diff.patch."""

from __future__ import annotations

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.patch import (
    PatchError,
    PatchHunk,
    build_hunks,
    format_patch,
    parse_patch_format,
)


# ---------------------------------------------------------------------------
# parse_patch_format
# ---------------------------------------------------------------------------

def test_parse_patch_format_none_returns_none():
    assert parse_patch_format(None) is None


def test_parse_patch_format_unified():
    assert parse_patch_format("unified") == "unified"


def test_parse_patch_format_case_insensitive():
    assert parse_patch_format("Unified") == "unified"


def test_parse_patch_format_raises_on_unknown():
    with pytest.raises(PatchError, match="Unknown patch format"):
        parse_patch_format("context")


# ---------------------------------------------------------------------------
# build_hunks
# ---------------------------------------------------------------------------

def test_build_hunks_empty_diff():
    assert build_hunks([]) == []


def test_build_hunks_added_row():
    event = RowAdded(key="1", row={"id": "1", "name": "Alice"})
    hunks = build_hunks([event])
    assert len(hunks) == 1
    assert hunks[0].change_type == "added"
    assert hunks[0].key == "1"
    assert "+ id: 1" in hunks[0].lines
    assert "+ name: Alice" in hunks[0].lines


def test_build_hunks_removed_row():
    event = RowRemoved(key="2", row={"id": "2", "name": "Bob"})
    hunks = build_hunks([event])
    assert hunks[0].change_type == "removed"
    assert "- name: Bob" in hunks[0].lines


def test_build_hunks_modified_row():
    event = RowModified(
        key="3",
        old_row={"id": "3", "name": "Carol"},
        new_row={"id": "3", "name": "Caroline"},
    )
    hunks = build_hunks([event])
    assert hunks[0].change_type == "modified"
    assert "- name: Carol" in hunks[0].lines
    assert "+ name: Caroline" in hunks[0].lines


def test_build_hunks_preserves_order():
    events = [
        RowAdded(key="a", row={"id": "a"}),
        RowRemoved(key="b", row={"id": "b"}),
    ]
    hunks = build_hunks(events)
    assert [h.change_type for h in hunks] == ["added", "removed"]


# ---------------------------------------------------------------------------
# format_patch
# ---------------------------------------------------------------------------

def test_format_patch_empty_returns_empty_string():
    assert format_patch([]) == ""


def test_format_patch_contains_header():
    hunk = PatchHunk(key="1", change_type="added", lines=["+ id: 1"])
    output = format_patch([hunk])
    assert "@@ added key=1 @@" in output


def test_format_patch_contains_lines():
    hunk = PatchHunk(key="1", change_type="added", lines=["+ id: 1", "+ name: Alice"])
    output = format_patch([hunk])
    assert "+ id: 1" in output
    assert "+ name: Alice" in output


def test_format_patch_multiple_hunks():
    hunks = [
        PatchHunk(key="1", change_type="added", lines=["+ id: 1"]),
        PatchHunk(key="2", change_type="removed", lines=["- id: 2"]),
    ]
    output = format_patch(hunks)
    assert "@@ added key=1 @@" in output
    assert "@@ removed key=2 @@" in output
