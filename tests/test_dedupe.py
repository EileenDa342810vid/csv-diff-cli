"""Tests for csv_diff.dedupe."""

import pytest

from csv_diff.dedupe import (
    DedupeError,
    DuplicateGroup,
    assert_no_duplicates,
    find_duplicates,
    format_duplicates,
)


ROWS = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
]

DUPE_ROWS = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "1", "name": "Duplicate Alice"},
    {"id": "2", "name": "Duplicate Bob"},
    {"id": "3", "name": "Carol"},
]


def test_find_duplicates_returns_empty_for_unique_keys():
    result = find_duplicates(ROWS, "id")
    assert result == []


def test_find_duplicates_detects_single_duplicate_group():
    rows = [
        {"id": "1", "name": "Alice"},
        {"id": "1", "name": "Alice2"},
        {"id": "2", "name": "Bob"},
    ]
    result = find_duplicates(rows, "id")
    assert len(result) == 1
    assert result[0].key == "1"
    assert result[0].count == 2


def test_find_duplicates_detects_multiple_groups():
    result = find_duplicates(DUPE_ROWS, "id")
    keys = {g.key for g in result}
    assert keys == {"1", "2"}


def test_find_duplicates_raises_on_missing_key_column():
    rows = [{"name": "Alice"}]
    with pytest.raises(DedupeError, match="missing key column"):
        find_duplicates(rows, "id")


def test_format_duplicates_returns_none_when_clean():
    result = format_duplicates([], "id", label="a.csv")
    assert result is None


def test_format_duplicates_contains_key_and_label():
    groups = find_duplicates(DUPE_ROWS, "id")
    report = format_duplicates(groups, "id", label="a.csv")
    assert report is not None
    assert "a.csv" in report
    assert "id" in report
    assert "'1'" in report
    assert "'2'" in report


def test_assert_no_duplicates_passes_for_unique():
    assert_no_duplicates(ROWS, "id")  # should not raise


def test_assert_no_duplicates_raises_for_dupes():
    with pytest.raises(DedupeError):
        assert_no_duplicates(DUPE_ROWS, "id", label="test.csv")
