"""Tests for csv_diff.reorder."""

import pytest

from csv_diff.reorder import (
    ReorderError,
    ColumnOrder,
    parse_reorder_columns,
    validate_reorder_columns,
    apply_reorder,
    reorder_rows,
)

HEADERS = ["id", "name", "region", "value"]


def test_parse_reorder_columns_none_returns_none():
    assert parse_reorder_columns(None) is None


def test_parse_reorder_columns_empty_string_returns_none():
    assert parse_reorder_columns("") is None
    assert parse_reorder_columns("   ") is None


def test_parse_reorder_columns_single():
    result = parse_reorder_columns("region")
    assert result == ColumnOrder(columns=["region"])


def test_parse_reorder_columns_multiple():
    result = parse_reorder_columns("region, value")
    assert result == ColumnOrder(columns=["region", "value"])


def test_parse_reorder_columns_raises_on_empty_entry():
    with pytest.raises(ReorderError, match="empty column entry"):
        parse_reorder_columns("region,,value")


def test_validate_reorder_columns_passes_for_known_columns():
    order = ColumnOrder(columns=["region", "id"])
    validate_reorder_columns(order, HEADERS)  # should not raise


def test_validate_reorder_columns_raises_on_unknown():
    order = ColumnOrder(columns=["nonexistent"])
    with pytest.raises(ReorderError, match="nonexistent"):
        validate_reorder_columns(order, HEADERS)


def test_apply_reorder_puts_listed_columns_first():
    row = {"id": "1", "name": "Alice", "region": "EU", "value": "42"}
    order = ColumnOrder(columns=["region", "value"])
    result = apply_reorder(row, order)
    keys = list(result.keys())
    assert keys[0] == "region"
    assert keys[1] == "value"


def test_apply_reorder_appends_remaining_columns():
    row = {"id": "1", "name": "Alice", "region": "EU", "value": "42"}
    order = ColumnOrder(columns=["value"])
    result = apply_reorder(row, order)
    keys = list(result.keys())
    assert keys[0] == "value"
    assert set(keys[1:]) == {"id", "name", "region"}


def test_apply_reorder_preserves_values():
    row = {"id": "7", "name": "Bob", "region": "US", "value": "99"}
    order = ColumnOrder(columns=["name"])
    result = apply_reorder(row, order)
    assert result == row


def test_reorder_rows_none_returns_unchanged():
    rows = [{"id": "1", "name": "Alice"}]
    assert reorder_rows(rows, None) is rows


def test_reorder_rows_applies_order_to_all_rows():
    rows = [
        {"id": "1", "name": "Alice", "region": "EU"},
        {"id": "2", "name": "Bob", "region": "US"},
    ]
    order = ColumnOrder(columns=["region"])
    result = reorder_rows(rows, order)
    for row in result:
        assert list(row.keys())[0] == "region"
