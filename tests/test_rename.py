"""Unit tests for csv_diff.rename."""

import pytest

from csv_diff.rename import (
    ColumnRename,
    RenameError,
    apply_renames,
    parse_renames,
    rename_rows,
    validate_renames,
)


def test_parse_renames_none_returns_none():
    assert parse_renames(None) is None


def test_parse_renames_empty_string_returns_none():
    assert parse_renames("") is None
    assert parse_renames("   ") is None


def test_parse_renames_single():
    result = parse_renames("old=new")
    assert result == ColumnRename(mapping={"old": "new"})


def test_parse_renames_multiple():
    result = parse_renames("a=A,b=B")
    assert result == ColumnRename(mapping={"a": "A", "b": "B"})


def test_parse_renames_strips_whitespace():
    result = parse_renames(" a = A , b = B ")
    assert result == ColumnRename(mapping={"a": "A", "b": "B"})


def test_parse_renames_raises_on_missing_equals():
    with pytest.raises(RenameError, match="expected old=new"):
        parse_renames("badspec")


def test_parse_renames_raises_on_empty_name():
    with pytest.raises(RenameError, match="empty name"):
        parse_renames("=new")


def test_validate_renames_passes_when_all_present():
    rename = ColumnRename(mapping={"id": "ID"})
    validate_renames(rename, ["id", "name"])  # no exception


def test_validate_renames_raises_on_missing_column():
    rename = ColumnRename(mapping={"missing": "X"})
    with pytest.raises(RenameError, match="missing"):
        validate_renames(rename, ["id", "name"])


def test_apply_renames_renames_matching_headers():
    rename = ColumnRename(mapping={"id": "ID", "name": "Name"})
    assert apply_renames(rename, ["id", "name", "age"]) == ["ID", "Name", "age"]


def test_apply_renames_leaves_unmatched_headers():
    rename = ColumnRename(mapping={"id": "ID"})
    assert apply_renames(rename, ["id", "other"]) == ["ID", "other"]


def test_rename_rows_renames_keys():
    rename = ColumnRename(mapping={"id": "ID"})
    rows = [{"id": "1", "name": "Alice"}]
    assert rename_rows(rename, rows) == [{"ID": "1", "name": "Alice"}]


def test_rename_rows_empty_list():
    rename = ColumnRename(mapping={"id": "ID"})
    assert rename_rows(rename, []) == []
