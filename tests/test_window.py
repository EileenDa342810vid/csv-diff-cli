"""Tests for csv_diff.window."""

from __future__ import annotations

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.window import (
    WindowError,
    WindowResult,
    compute_window,
    format_window,
    parse_window_size,
)


# ---------------------------------------------------------------------------
# parse_window_size
# ---------------------------------------------------------------------------

def test_parse_window_size_none_returns_none():
    assert parse_window_size(None) is None


def test_parse_window_size_integer_passthrough():
    assert parse_window_size(3) == 3


def test_parse_window_size_string_integer():
    assert parse_window_size("5") == 5


def test_parse_window_size_raises_on_non_integer():
    with pytest.raises(WindowError):
        parse_window_size("abc")


def test_parse_window_size_raises_on_zero():
    with pytest.raises(WindowError):
        parse_window_size(0)


def test_parse_window_size_raises_on_negative():
    with pytest.raises(WindowError):
        parse_window_size(-2)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(key="k", old_row=old, new_row=new)


# ---------------------------------------------------------------------------
# compute_window
# ---------------------------------------------------------------------------

def test_empty_diff_returns_empty_result():
    result = compute_window([], "price", 3)
    assert result.values == []
    assert result.means == []


def test_single_value_window():
    events = [_added({"price": "10.0"})]
    result = compute_window(events, "price", 3)
    assert result.values == [10.0]
    assert result.means == [10.0]
    assert result.mins == [10.0]
    assert result.maxs == [10.0]


def test_window_size_one_equals_values():
    events = [_added({"price": "1"}), _added({"price": "2"}), _added({"price": "3"})]
    result = compute_window(events, "price", 1)
    assert result.means == [1.0, 2.0, 3.0]
    assert result.mins == [1.0, 2.0, 3.0]


def test_rolling_mean_correct():
    events = [
        _added({"v": "2"}),
        _added({"v": "4"}),
        _added({"v": "6"}),
    ]
    result = compute_window(events, "v", 2)
    assert result.means == [2.0, 3.0, 5.0]


def test_rolling_min_max_correct():
    events = [
        _added({"v": "10"}),
        _added({"v": "2"}),
        _added({"v": "8"}),
    ]
    result = compute_window(events, "v", 2)
    assert result.mins == [10.0, 2.0, 2.0]
    assert result.maxs == [10.0, 10.0, 8.0]


def test_uses_new_row_for_modified_events():
    events = [_modified({"v": "1"}, {"v": "99"})]
    result = compute_window(events, "v", 1)
    assert result.values == [99.0]


def test_skips_non_numeric_values():
    events = [
        _added({"v": "hello"}),
        _added({"v": "5"}),
    ]
    result = compute_window(events, "v", 2)
    assert result.values == [5.0]


def test_skips_missing_column():
    events = [_added({"other": "3"})]
    result = compute_window(events, "price", 2)
    assert result.values == []


# ---------------------------------------------------------------------------
# format_window
# ---------------------------------------------------------------------------

def test_format_window_no_data():
    result = WindowResult(column="x", window_size=3, values=[], means=[], mins=[], maxs=[])
    out = format_window(result)
    assert "no numeric data" in out


def test_format_window_contains_column_name():
    events = [_added({"score": "7"})]
    result = compute_window(events, "score", 2)
    out = format_window(result)
    assert "score" in out
    assert "7" in out or "7.0" in out
