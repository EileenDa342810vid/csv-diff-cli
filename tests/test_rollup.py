"""Tests for csv_diff.rollup."""
import pytest
from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.rollup import (
    ColumnRollup,
    format_rollup,
    parse_rollup_column,
    rollup_diff,
)


def _added(row): return RowAdded(row=row)
def _removed(row): return RowRemoved(row=row)
def _modified(old, new): return RowModified(key="k", old_row=old, new_row=new)


def test_parse_rollup_column_none_returns_none():
    assert parse_rollup_column(None) is None


def test_parse_rollup_column_empty_returns_none():
    assert parse_rollup_column("  ") is None


def test_parse_rollup_column_strips_whitespace():
    assert parse_rollup_column(" amount ") == "amount"


def test_empty_diff_returns_zero_rollup():
    r = rollup_diff([], "amount")
    assert r.total_added == 0.0
    assert r.total_removed == 0.0
    assert r.total_delta == 0.0
    assert r.changed_rows == 0


def test_added_row_increments_added():
    events = [_added({"id": "1", "amount": "50"})]
    r = rollup_diff(events, "amount")
    assert r.total_added == 50.0
    assert r.total_delta == 50.0
    assert r.changed_rows == 1


def test_removed_row_increments_removed():
    events = [_removed({"id": "1", "amount": "30"})]
    r = rollup_diff(events, "amount")
    assert r.total_removed == 30.0
    assert r.total_delta == -30.0


def test_modified_row_computes_delta():
    events = [_modified({"id": "1", "amount": "10"}, {"id": "1", "amount": "25"})]
    r = rollup_diff(events, "amount")
    assert r.total_delta == pytest.approx(15.0)
    assert r.changed_rows == 1


def test_non_numeric_values_treated_as_zero():
    events = [_added({"id": "1", "amount": "n/a"})]
    r = rollup_diff(events, "amount")
    assert r.total_added == 0.0


def test_missing_column_treated_as_zero():
    events = [_added({"id": "1"})]
    r = rollup_diff(events, "amount")
    assert r.total_added == 0.0


def test_format_rollup_contains_column_name():
    r = ColumnRollup(column="revenue", total_added=100, total_removed=20, total_delta=80, changed_rows=3)
    out = format_rollup(r)
    assert "revenue" in out
    assert "+100" in out
    assert "80" in out
