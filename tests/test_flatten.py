"""Tests for csv_diff.flatten."""

import pytest
from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.flatten import (
    FlatRecord,
    FlattenError,
    flatten_diff,
    format_flat_records,
)


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(old_row=old, new_row=new)


def test_empty_diff_returns_empty_list():
    assert flatten_diff([]) == []


def test_added_row_produces_one_record_per_column():
    events = [_added({"id": "1", "name": "Alice", "age": "30"})]
    records = flatten_diff(events)
    assert len(records) == 3
    assert all(r.change_type == "added" for r in records)
    assert all(r.old_value is None for r in records)
    cols = {r.column for r in records}
    assert cols == {"id", "name", "age"}


def test_removed_row_produces_one_record_per_column():
    events = [_removed({"id": "2", "name": "Bob"})]
    records = flatten_diff(events)
    assert len(records) == 2
    assert all(r.change_type == "removed" for r in records)
    assert all(r.new_value is None for r in records)


def test_modified_row_only_includes_changed_columns():
    old = {"id": "3", "name": "Carol", "age": "25"}
    new = {"id": "3", "name": "Caroline", "age": "25"}
    events = [_modified(old, new)]
    records = flatten_diff(events)
    assert len(records) == 1
    assert records[0].change_type == "modified"
    assert records[0].column == "name"
    assert records[0].old_value == "Carol"
    assert records[0].new_value == "Caroline"


def test_modified_row_no_changes_produces_no_records():
    row = {"id": "4", "name": "Dave"}
    events = [_modified(row, row.copy())]
    assert flatten_diff(events) == []


def test_key_uses_first_column_value():
    events = [_added({"id": "99", "name": "Eve"})]
    records = flatten_diff(events)
    assert all(r.key == "99" for r in records)


def test_unknown_event_type_raises():
    with pytest.raises(FlattenError):
        flatten_diff([object()])


def test_format_flat_records_no_changes():
    result = format_flat_records([])
    assert result == "(no changes)"


def test_format_flat_records_contains_headers():
    events = [_added({"id": "1", "val": "x"})]
    records = flatten_diff(events)
    output = format_flat_records(records)
    assert "TYPE" in output
    assert "COLUMN" in output
    assert "OLD" in output
    assert "NEW" in output


def test_format_flat_records_contains_data():
    events = [_removed({"id": "5", "city": "Paris"})]
    records = flatten_diff(events)
    output = format_flat_records(records)
    assert "removed" in output
    assert "Paris" in output
