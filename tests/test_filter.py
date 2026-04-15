"""Tests for csv_diff.filter module."""

import pytest

from csv_diff.filter import (
    FilterError,
    filter_row,
    filter_rows,
    parse_columns,
    validate_columns,
)


# ---------------------------------------------------------------------------
# parse_columns
# ---------------------------------------------------------------------------

def test_parse_columns_none_returns_none():
    assert parse_columns(None) is None


def test_parse_columns_single():
    assert parse_columns("name") == ["name"]


def test_parse_columns_multiple():
    assert parse_columns("id, name, age") == ["id", "name", "age"]


def test_parse_columns_raises_on_empty_entry():
    with pytest.raises(FilterError, match="empty entries"):
        parse_columns("id,,name")


# ---------------------------------------------------------------------------
# validate_columns
# ---------------------------------------------------------------------------

def test_validate_columns_all_present():
    # Should not raise
    validate_columns(["id", "name"], ["id", "name", "age"])


def test_validate_columns_missing_raises():
    with pytest.raises(FilterError, match="Unknown column"):
        validate_columns(["id", "salary"], ["id", "name"])


def test_validate_columns_error_lists_available():
    with pytest.raises(FilterError, match="id, name"):
        validate_columns(["missing"], ["id", "name"])


# ---------------------------------------------------------------------------
# filter_row
# ---------------------------------------------------------------------------

def test_filter_row_none_keeps_all():
    row = {"id": "1", "name": "Alice", "age": "30"}
    assert filter_row(row, None) == row


def test_filter_row_subset():
    row = {"id": "1", "name": "Alice", "age": "30"}
    assert filter_row(row, ["id", "name"]) == {"id": "1", "name": "Alice"}


def test_filter_row_returns_copy():
    row = {"id": "1", "name": "Alice"}
    result = filter_row(row, None)
    result["id"] = "99"
    assert row["id"] == "1"


# ---------------------------------------------------------------------------
# filter_rows
# ---------------------------------------------------------------------------

def test_filter_rows_applies_to_all():
    rows = [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
    ]
    result = filter_rows(rows, ["id", "name"])
    assert result == [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]


def test_filter_rows_empty_list():
    assert filter_rows([], ["id"]) == []
