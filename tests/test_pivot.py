"""Tests for csv_diff.pivot."""

from __future__ import annotations

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.pivot import ColumnPivot, PivotError, format_pivot, pivot_by_column


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(row: dict) -> RowAdded:
    return RowAdded(row=row)


def _removed(row: dict) -> RowRemoved:
    return RowRemoved(row=row)


def _modified(old: dict, new: dict) -> RowModified:
    return RowModified(old_row=old, new_row=new)


# ---------------------------------------------------------------------------
# pivot_by_column
# ---------------------------------------------------------------------------

def test_empty_diff_returns_empty_dict():
    assert pivot_by_column([]) == {}


def test_added_row_populates_added_values():
    diff = [_added({"id": "1", "name": "Alice"})]
    pivots = pivot_by_column(diff)
    assert "name" in pivots
    assert "Alice" in pivots["name"].added_values


def test_removed_row_populates_removed_values():
    diff = [_removed({"id": "2", "name": "Bob"})]
    pivots = pivot_by_column(diff)
    assert "Bob" in pivots["name"].removed_values


def test_modified_row_only_tracks_changed_columns():
    diff = [
        _modified(
            {"id": "1", "name": "Alice", "age": "30"},
            {"id": "1", "name": "Alicia", "age": "30"},
        )
    ]
    pivots = pivot_by_column(diff)
    assert "name" in pivots
    assert "age" not in pivots
    assert ("Alice", "Alicia") in pivots["name"].modified_pairs


def test_modified_row_records_old_and_new_values():
    diff = [_modified({"id": "1", "score": "10"}, {"id": "1", "score": "20"})]
    pivots = pivot_by_column(diff)
    assert pivots["score"].modified_pairs == [("10", "20")]


def test_total_changes_sums_all_event_types():
    cp = ColumnPivot(column="x")
    cp.added_values = ["a", "b"]
    cp.removed_values = ["c"]
    cp.modified_pairs = [("d", "e"), ("f", "g")]
    assert cp.total_changes == 5


def test_raises_on_unknown_event_type():
    with pytest.raises(PivotError, match="Unrecognised"):
        pivot_by_column([object()])  # type: ignore[list-item]


def test_multiple_events_accumulate_per_column():
    diff = [
        _added({"id": "1", "city": "Paris"}),
        _added({"id": "2", "city": "Rome"}),
    ]
    pivots = pivot_by_column(diff)
    assert len(pivots["city"].added_values) == 2


# ---------------------------------------------------------------------------
# format_pivot
# ---------------------------------------------------------------------------

def test_format_pivot_empty_returns_message():
    assert format_pivot({}) == "No column changes."


def test_format_pivot_contains_column_name():
    diff = [_added({"status": "active"})]
    output = format_pivot(pivot_by_column(diff))
    assert "status" in output


def test_format_pivot_added_prefixed_with_plus():
    diff = [_added({"role": "admin"})]
    output = format_pivot(pivot_by_column(diff))
    assert "+ admin" in output


def test_format_pivot_removed_prefixed_with_minus():
    diff = [_removed({"role": "guest"})]
    output = format_pivot(pivot_by_column(diff))
    assert "- guest" in output


def test_format_pivot_modified_shows_arrow():
    diff = [_modified({"level": "1"}, {"level": "2"})]
    output = format_pivot(pivot_by_column(diff))
    assert "->" in output
