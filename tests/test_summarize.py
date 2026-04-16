"""Tests for csv_diff.summarize."""

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.summarize import (
    ChangeSummary,
    ColumnFrequency,
    compute_column_frequencies,
    format_column_summary,
    summarize_columns,
)


def _added(key="1"):
    return RowAdded(key=key, row={"id": key, "name": "Alice"})


def _removed(key="2"):
    return RowRemoved(key=key, row={"id": key, "name": "Bob"})


def _modified(key="3", changes=None):
    if changes is None:
        changes = {"name": ("Old", "New")}
    return RowModified(key=key, before={"id": key}, after={"id": key}, changes=changes)


def test_empty_diff_returns_zero_counts():
    summary = summarize_columns([])
    assert summary.added == 0
    assert summary.removed == 0
    assert summary.modified == 0
    assert summary.total_rows_changed == 0
    assert summary.column_frequencies == []


def test_counts_added_rows():
    summary = summarize_columns([_added("1"), _added("2")])
    assert summary.added == 2
    assert summary.total_rows_changed == 2


def test_counts_removed_rows():
    summary = summarize_columns([_removed()])
    assert summary.removed == 1


def test_counts_modified_rows():
    summary = summarize_columns([_modified(), _modified(key="4")])
    assert summary.modified == 2


def test_total_is_sum_of_all_types():
    diff = [_added(), _removed(), _modified()]
    summary = summarize_columns(diff)
    assert summary.total_rows_changed == 3


def test_compute_column_frequencies_empty():
    assert compute_column_frequencies([]) == {}


def test_compute_column_frequencies_single_column():
    diff = [_modified(changes={"name": ("A", "B")}), _modified(key="4", changes={"name": ("C", "D")})]
    freqs = compute_column_frequencies(diff)
    assert freqs == {"name": 2}


def test_compute_column_frequencies_multiple_columns():
    diff = [
        _modified(changes={"name": ("A", "B"), "age": ("1", "2")}),
        _modified(key="4", changes={"age": ("3", "4")}),
    ]
    freqs = compute_column_frequencies(diff)
    assert freqs["age"] == 2
    assert freqs["name"] == 1


def test_column_frequencies_sorted_by_count_descending():
    diff = [
        _modified(key="1", changes={"x": ("a", "b")}),
        _modified(key="2", changes={"x": ("c", "d"), "y": ("e", "f")}),
        _modified(key="3", changes={"x": ("g", "h")}),
    ]
    summary = summarize_columns(diff)
    assert summary.column_frequencies[0].column == "x"
    assert summary.column_frequencies[0].change_count == 3


def test_percentage_calculated_against_modified_rows():
    diff = [
        _modified(key="1", changes={"name": ("a", "b")}),
        _modified(key="2", changes={"name": ("c", "d")}),
        _modified(key="3", changes={"age": ("1", "2")}),
    ]
    summary = summarize_columns(diff)
    name_cf = next(cf for cf in summary.column_frequencies if cf.column == "name")
    assert name_cf.percentage == pytest.approx(66.7, abs=0.1)


def test_format_column_summary_contains_header():
    summary = summarize_columns([])
    output = format_column_summary(summary)
    assert "=== Change Summary ===" in output


def test_format_column_summary_lists_columns():
    diff = [_modified(changes={"email": ("old@x.com", "new@x.com")})]
    summary = summarize_columns(diff)
    output = format_column_summary(summary)
    assert "email" in output
    assert "100.0%" in output


def test_format_column_summary_no_columns_section_when_no_modifications():
    diff = [_added(), _removed()]
    summary = summarize_columns(diff)
    output = format_column_summary(summary)
    assert "Modified columns" not in output
