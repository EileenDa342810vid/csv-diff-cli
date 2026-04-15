"""Tests for csv_diff.highlight field-level diffing."""
import pytest

from csv_diff.highlight import (
    FieldDiff,
    HighlightError,
    diff_fields,
    format_all_field_diffs,
    format_field_diff,
)


# ---------------------------------------------------------------------------
# diff_fields
# ---------------------------------------------------------------------------

def test_diff_fields_returns_empty_for_identical_rows():
    row = {"id": "1", "name": "Alice", "age": "30"}
    assert diff_fields(row, row.copy()) == []


def test_diff_fields_detects_single_change():
    old = {"id": "1", "name": "Alice", "age": "30"}
    new = {"id": "1", "name": "Alice", "age": "31"}
    result = diff_fields(old, new)
    assert len(result) == 1
    assert result[0] == FieldDiff(column="age", old_value="30", new_value="31")


def test_diff_fields_detects_multiple_changes():
    old = {"id": "1", "name": "Alice", "city": "NYC"}
    new = {"id": "1", "name": "Bob",   "city": "LA"}
    result = diff_fields(old, new)
    columns_changed = {f.column for f in result}
    assert columns_changed == {"name", "city"}


def test_diff_fields_preserves_column_order():
    old = {"a": "1", "b": "2", "c": "3"}
    new = {"a": "9", "b": "2", "c": "9"}
    result = diff_fields(old, new)
    assert [f.column for f in result] == ["a", "c"]


def test_diff_fields_raises_on_mismatched_columns():
    old = {"id": "1", "name": "Alice"}
    new = {"id": "1", "email": "a@b.com"}
    with pytest.raises(HighlightError, match="different columns"):
        diff_fields(old, new)


# ---------------------------------------------------------------------------
# format_field_diff
# ---------------------------------------------------------------------------

def test_format_field_diff_no_color():
    field = FieldDiff(column="age", old_value="30", new_value="31")
    line = format_field_diff(field, use_color=False)
    assert "age" in line
    assert "30" in line
    assert "31" in line
    assert "->" in line


def test_format_field_diff_with_color_contains_ansi():
    field = FieldDiff(column="score", old_value="100", new_value="200")
    line = format_field_diff(field, use_color=True)
    # ANSI escape sequences start with \x1b[
    assert "\x1b[" in line


def test_format_field_diff_indented():
    field = FieldDiff(column="x", old_value="a", new_value="b")
    line = format_field_diff(field, use_color=False)
    assert line.startswith("  ")


# ---------------------------------------------------------------------------
# format_all_field_diffs
# ---------------------------------------------------------------------------

def test_format_all_field_diffs_empty_on_identical():
    row = {"id": "1", "val": "same"}
    assert format_all_field_diffs(row, row.copy()) == []


def test_format_all_field_diffs_returns_one_line_per_change():
    old = {"id": "1", "a": "x", "b": "y"}
    new = {"id": "1", "a": "X", "b": "Y"}
    lines = format_all_field_diffs(old, new)
    assert len(lines) == 2


def test_format_all_field_diffs_propagates_color_flag():
    old = {"v": "old"}
    new = {"v": "new"}
    lines_color = format_all_field_diffs(old, new, use_color=True)
    lines_plain = format_all_field_diffs(old, new, use_color=False)
    assert "\x1b[" in lines_color[0]
    assert "\x1b[" not in lines_plain[0]
