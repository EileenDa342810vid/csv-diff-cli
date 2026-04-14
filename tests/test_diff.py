"""Tests for csv_diff.diff and csv_diff.formatter."""

import pytest
from csv_diff.diff import RowAdded, RowModified, RowRemoved, diff_csv
from csv_diff.formatter import format_diff


OLD_ROWS = [
    {"id": "1", "name": "Alice", "score": "90"},
    {"id": "2", "name": "Bob", "score": "85"},
    {"id": "3", "name": "Carol", "score": "78"},
]

NEW_ROWS = [
    {"id": "1", "name": "Alice", "score": "95"},  # modified
    {"id": "2", "name": "Bob", "score": "85"},   # unchanged
    {"id": "4", "name": "Dave", "score": "88"},   # added
    # id=3 removed
]


def test_detects_added_row():
    results = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    added = [r for r in results if isinstance(r, RowAdded)]
    assert len(added) == 1
    assert added[0].key == "4"
    assert added[0].row["name"] == "Dave"


def test_detects_removed_row():
    results = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    removed = [r for r in results if isinstance(r, RowRemoved)]
    assert len(removed) == 1
    assert removed[0].key == "3"


def test_detects_modified_row():
    results = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    modified = [r for r in results if isinstance(r, RowModified)]
    assert len(modified) == 1
    assert modified[0].key == "1"
    assert "score" in modified[0].changed_columns
    assert modified[0].old_row["score"] == "90"
    assert modified[0].new_row["score"] == "95"


def test_no_diff_on_identical_data():
    results = diff_csv(OLD_ROWS, OLD_ROWS, key_column="id")
    assert results == []


def test_format_diff_no_changes():
    output = format_diff([], use_color=False)
    assert output == "No differences found."


def test_format_diff_contains_key_info():
    results = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    output = format_diff(results, use_color=False)
    assert "Added row (key=4)" in output
    assert "Removed row (key=3)" in output
    assert "Modified row (key=1)" in output
    assert "score" in output


def test_format_diff_marks_changed_columns():
    results = diff_csv(OLD_ROWS, NEW_ROWS, key_column="id")
    output = format_diff(results, use_color=False)
    # Changed column should be marked with '*'
    assert "* score" in output
