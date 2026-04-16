"""Tests for csv_diff.profile."""
import pytest
from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.profile import (
    ProfileError,
    ColumnProfile,
    DiffProfile,
    profile_diff,
    format_profile,
)

HEADERS = ["id", "name", "score"]


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(key=old["id"], old_row=old, new_row=new)


def test_empty_diff_returns_empty_profile():
    prof = profile_diff([], HEADERS)
    assert prof.total_rows_a == 0
    assert prof.total_rows_b == 0


def test_added_row_increments_b():
    events = [_added({"id": "1", "name": "Alice", "score": "10"})]
    prof = profile_diff(events, HEADERS)
    assert prof.total_rows_b == 1
    assert prof.total_rows_a == 0


def test_removed_row_increments_a():
    events = [_removed({"id": "1", "name": "Alice", "score": "10"})]
    prof = profile_diff(events, HEADERS)
    assert prof.total_rows_a == 1
    assert prof.total_rows_b == 0


def test_modified_row_increments_both():
    events = [_modified(
        {"id": "1", "name": "Alice", "score": "10"},
        {"id": "1", "name": "Alice", "score": "20"},
    )]
    prof = profile_diff(events, HEADERS)
    assert prof.total_rows_a == 1
    assert prof.total_rows_b == 1


def test_modified_row_counts_column_change():
    events = [_modified(
        {"id": "1", "name": "Alice", "score": "10"},
        {"id": "1", "name": "Bob", "score": "10"},
    )]
    prof = profile_diff(events, HEADERS)
    assert prof.columns["name"].changes == 1
    assert prof.columns["score"].changes == 0


def test_top_new_values_populated():
    events = [
        _added({"id": "1", "name": "Alice", "score": "10"}),
        _added({"id": "2", "name": "Alice", "score": "20"}),
        _added({"id": "3", "name": "Bob", "score": "10"}),
    ]
    prof = profile_diff(events, HEADERS)
    assert prof.columns["name"].top_new_values[0] == "Alice"


def test_unique_values_counted():
    events = [
        _added({"id": "1", "name": "Alice", "score": "10"}),
        _added({"id": "2", "name": "Alice", "score": "20"}),
    ]
    prof = profile_diff(events, HEADERS)
    assert prof.columns["name"].unique_new_values == 1
    assert prof.columns["score"].unique_new_values == 2


def test_invalid_headers_raises():
    with pytest.raises(ProfileError):
        profile_diff([], "id,name")


def test_format_profile_contains_header():
    prof = profile_diff([], HEADERS)
    out = format_profile(prof)
    assert "Column" in out
    assert "Changes" in out


def test_format_profile_lists_columns():
    events = [_modified(
        {"id": "1", "name": "Alice", "score": "10"},
        {"id": "1", "name": "Bob", "score": "10"},
    )]
    prof = profile_diff(events, HEADERS)
    out = format_profile(prof)
    assert "name" in out
    assert "score" in out
