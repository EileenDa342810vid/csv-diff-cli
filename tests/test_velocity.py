"""Unit tests for csv_diff.velocity."""

from __future__ import annotations

import pytest

from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.velocity import (
    parse_velocity_column,
    compute_velocity,
    format_velocity,
    VelocityResult,
    ColumnVelocity,
)


def _added(row: dict) -> RowAdded:
    return RowAdded(row=row)


def _removed(row: dict) -> RowRemoved:
    return RowRemoved(row=row)


def _modified(old: dict, new: dict) -> RowModified:
    return RowModified(old_row=old, new_row=new)


HEADERS = ["id", "name", "score"]


def test_parse_velocity_column_none_returns_none():
    assert parse_velocity_column(None) is None


def test_parse_velocity_column_empty_returns_none():
    assert parse_velocity_column("") is None
    assert parse_velocity_column("   ") is None


def test_parse_velocity_column_strips_whitespace():
    assert parse_velocity_column("  score  ") == "score"


def test_empty_diff_returns_zero_counts():
    result = compute_velocity([], HEADERS)
    assert result.total_rows == 0
    assert all(c.changes == 0 for c in result.columns)


def test_added_row_increments_non_empty_columns():
    events = [_added({"id": "1", "name": "Alice", "score": ""})]
    result = compute_velocity(events, HEADERS)
    by_col = {c.column: c.changes for c in result.columns}
    assert by_col["id"] == 1
    assert by_col["name"] == 1
    assert by_col["score"] == 0  # empty value not counted


def test_removed_row_increments_non_empty_columns():
    events = [_removed({"id": "2", "name": "Bob", "score": "99"})]
    result = compute_velocity(events, HEADERS)
    by_col = {c.column: c.changes for c in result.columns}
    assert by_col["score"] == 1


def test_modified_row_counts_changed_columns_only():
    old = {"id": "3", "name": "Carol", "score": "80"}
    new = {"id": "3", "name": "Carol", "score": "95"}
    result = compute_velocity([_modified(old, new)], HEADERS)
    by_col = {c.column: c.changes for c in result.columns}
    assert by_col["score"] == 1
    assert by_col["name"] == 0
    assert by_col["id"] == 0


def test_rate_computed_correctly():
    events = [
        _modified(
            {"id": "1", "name": "A", "score": "1"},
            {"id": "1", "name": "B", "score": "2"},
        ),
        _modified(
            {"id": "2", "name": "C", "score": "3"},
            {"id": "2", "name": "C", "score": "4"},
        ),
    ]
    result = compute_velocity(events, HEADERS)
    by_col = {c.column: c for c in result.columns}
    assert by_col["name"].changes == 1
    assert by_col["name"]._rate == pytest.approx(0.5)
    assert by_col["score"].changes == 2
    assert by_col["score"]._rate == pytest.approx(1.0)


def test_fastest_returns_most_changed_column():
    events = [
        _modified(
            {"id": "1", "name": "A", "score": "10"},
            {"id": "1", "name": "B", "score": "20"},
        )
    ]
    result = compute_velocity(events, HEADERS)
    fastest = result.fastest()
    assert fastest is not None
    assert fastest.changes >= 1


def test_format_velocity_contains_header():
    result = compute_velocity([], HEADERS)
    output = format_velocity(result)
    assert "Change Velocity" in output
    assert "Total rows examined" in output


def test_format_velocity_lists_all_columns():
    result = compute_velocity([], HEADERS)
    output = format_velocity(result)
    for h in HEADERS:
        assert h in output
