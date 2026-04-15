"""Tests for csv_diff.sorter."""

import pytest

from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.sorter import SortError, parse_sort_key, sort_diff


# ---------------------------------------------------------------------------
# parse_sort_key
# ---------------------------------------------------------------------------

def test_parse_sort_key_none_returns_none():
    assert parse_sort_key(None) is None


def test_parse_sort_key_valid_values():
    assert parse_sort_key("key") == "key"
    assert parse_sort_key("type") == "type"
    assert parse_sort_key("column") == "column"


def test_parse_sort_key_normalises_case():
    assert parse_sort_key("KEY") == "key"
    assert parse_sort_key("Type") == "type"


def test_parse_sort_key_raises_on_unknown():
    with pytest.raises(SortError, match="Unknown sort key"):
        parse_sort_key("invalid")


# ---------------------------------------------------------------------------
# sort_diff helpers
# ---------------------------------------------------------------------------

_CHANGES = [
    RowModified(key="charlie", diffs={"age": ("30", "31")}),
    RowAdded(key="alice", row={"name": "alice", "age": "25"}),
    RowRemoved(key="bob", row={"name": "bob", "age": "40"}),
    RowModified(key="dave", diffs={"city": ("NY", "LA")}),
]


def test_sort_none_preserves_order():
    result = sort_diff(_CHANGES, None)
    assert result == list(_CHANGES)


def test_sort_by_key():
    result = sort_diff(_CHANGES, "key")
    keys = [c.key for c in result]
    assert keys == sorted(keys)


def test_sort_by_type_groups_correctly():
    result = sort_diff(_CHANGES, "type")
    types = [type(c).__name__ for c in result]
    # All RowAdded before RowRemoved before RowModified
    added_indices = [i for i, t in enumerate(types) if t == "RowAdded"]
    removed_indices = [i for i, t in enumerate(types) if t == "RowRemoved"]
    modified_indices = [i for i, t in enumerate(types) if t == "RowModified"]
    assert max(added_indices) < min(removed_indices)
    assert max(removed_indices) < min(modified_indices)


def test_sort_by_column_puts_modified_first():
    result = sort_diff(_CHANGES, "column")
    # Modified rows (with column info) should come before added/removed
    first_non_modified = next(
        (i for i, c in enumerate(result) if not isinstance(c, RowModified)), len(result)
    )
    for c in result[:first_non_modified]:
        assert isinstance(c, RowModified)


def test_sort_by_column_orders_by_first_changed_column():
    changes = [
        RowModified(key="z", diffs={"zebra": ("1", "2")}),
        RowModified(key="a", diffs={"apple": ("x", "y")}),
    ]
    result = sort_diff(changes, "column")
    assert result[0].key == "a"  # 'apple' < 'zebra'
    assert result[1].key == "z"


def test_sort_does_not_mutate_input():
    original = list(_CHANGES)
    sort_diff(_CHANGES, "key")
    assert _CHANGES == original
