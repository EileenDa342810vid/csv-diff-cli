"""Tests for csv_diff.stats module."""
import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.stats import DiffStats, compute_stats, format_stats


def _added(key: str) -> RowAdded:
    return RowAdded(key=key, row={"id": key, "name": "X"})


def _removed(key: str) -> RowRemoved:
    return RowRemoved(key=key, row={"id": key, "name": "Y"})


def _modified(key: str, cols: list[str]) -> RowModified:
    changes = {c: ("old", "new") for c in cols}
    return RowModified(
        key=key,
        old_row={"id": key},
        new_row={"id": key},
        changes=changes,
    )


def test_empty_diff_has_no_changes():
    stats = compute_stats([])
    assert not stats.has_changes
    assert stats.total_changes == 0


def test_counts_added():
    stats = compute_stats([_added("1"), _added("2")])
    assert stats.added == 2
    assert stats.removed == 0
    assert stats.modified == 0


def test_counts_removed():
    stats = compute_stats([_removed("1")])
    assert stats.removed == 1


def test_counts_modified():
    stats = compute_stats([_modified("1", ["name", "age"])])
    assert stats.modified == 1
    assert stats.modified_columns == {"name": 1, "age": 1}


def test_modified_column_accumulates():
    diff = [_modified("1", ["name"]), _modified("2", ["name", "city"])]
    stats = compute_stats(diff)
    assert stats.modified_columns["name"] == 2
    assert stats.modified_columns["city"] == 1


def test_unchanged_rows():
    stats = compute_stats([_added("1")], total_rows=5)
    assert stats.unchanged == 4


def test_unchanged_never_negative():
    stats = compute_stats([_added("1"), _added("2"), _added("3")], total_rows=1)
    assert stats.unchanged == 0


def test_format_stats_no_changes():
    stats = DiffStats()
    output = format_stats(stats)
    assert "No differences" in output


def test_format_stats_with_changes():
    stats = compute_stats(
        [_added("1"), _removed("2"), _modified("3", ["col"])]
    )
    output = format_stats(stats)
    assert "Added rows   : 1" in output
    assert "Removed rows : 1" in output
    assert "Modified rows: 1" in output
    assert "col: 1 change" in output


def test_format_stats_columns_sorted_by_count():
    diff = [
        _modified("1", ["a", "b"]),
        _modified("2", ["b"]),
    ]
    stats = compute_stats(diff)
    output = format_stats(stats)
    b_pos = output.index("b:")
    a_pos = output.index("a:")
    assert b_pos < a_pos  # b has higher count, appears first
