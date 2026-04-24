"""Tests for csv_diff.outlier."""
from __future__ import annotations

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.outlier import (
    OutlierError,
    detect_outliers,
    format_outliers,
    parse_outlier_columns,
    parse_z_threshold,
)


# ---------------------------------------------------------------------------
# parse_outlier_columns
# ---------------------------------------------------------------------------

def test_parse_outlier_columns_none_returns_none():
    assert parse_outlier_columns(None) is None


def test_parse_outlier_columns_empty_string_returns_none():
    assert parse_outlier_columns("") is None


def test_parse_outlier_columns_single():
    assert parse_outlier_columns("price") == ["price"]


def test_parse_outlier_columns_multiple():
    assert parse_outlier_columns("price, qty") == ["price", "qty"]


def test_parse_outlier_columns_raises_on_empty_entry():
    with pytest.raises(OutlierError):
        parse_outlier_columns("price,,qty")


# ---------------------------------------------------------------------------
# parse_z_threshold
# ---------------------------------------------------------------------------

def test_parse_z_threshold_none_returns_default():
    assert parse_z_threshold(None) == 3.0


def test_parse_z_threshold_float_passthrough():
    assert parse_z_threshold(2.5) == 2.5


def test_parse_z_threshold_raises_on_zero():
    with pytest.raises(OutlierError):
        parse_z_threshold(0)


def test_parse_z_threshold_raises_on_negative():
    with pytest.raises(OutlierError):
        parse_z_threshold(-1.0)


def test_parse_z_threshold_raises_on_non_numeric():
    with pytest.raises(OutlierError):
        parse_z_threshold("high")


# ---------------------------------------------------------------------------
# detect_outliers
# ---------------------------------------------------------------------------

def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(key="k", old_row=old, new_row=new)


def test_empty_diff_returns_result_with_no_outliers():
    results = detect_outliers([], ["price"])
    assert results["price"].count == 0


def test_no_outliers_in_uniform_data():
    events = [_added({"price": str(i)}) for i in range(10)]
    results = detect_outliers(events, ["price"])
    assert results["price"].count == 0


def test_detects_obvious_outlier():
    # 99 values near 0, one extreme outlier
    events = [_added({"price": "0"}) for _ in range(9)]
    events.append(_added({"price": "1000"}))
    results = detect_outliers(events, ["price"], z_threshold=2.0)
    assert results["price"].count >= 1


def test_non_numeric_values_are_skipped():
    events = [
        _added({"price": "abc"}),
        _added({"price": "1"}),
        _added({"price": "2"}),
    ]
    # Should not raise
    results = detect_outliers(events, ["price"])
    assert "price" in results


def test_modified_rows_both_sides_checked():
    events = [
        _modified({"price": "1"}, {"price": "1000"}),
    ] + [_added({"price": str(i)}) for i in range(8)]
    results = detect_outliers(events, ["price"], z_threshold=2.0)
    # 1000 should be flagged
    assert results["price"].count >= 1


def test_removed_rows_included_in_detection():
    events = [_removed({"price": str(i)}) for i in range(9)]
    events.append(_removed({"price": "9999"}))
    results = detect_outliers(events, ["price"], z_threshold=2.0)
    assert results["price"].count >= 1


def test_result_mean_is_correct():
    events = [_added({"v": str(i)}) for i in [2, 4, 6]]
    results = detect_outliers(events, ["v"])
    assert abs(results["v"].mean - 4.0) < 1e-9


# ---------------------------------------------------------------------------
# format_outliers
# ---------------------------------------------------------------------------

def test_format_outliers_none_when_empty():
    assert format_outliers({}) is None


def test_format_outliers_contains_column_name():
    events = [_added({"price": str(i)}) for i in range(9)]
    events.append(_added({"price": "9999"}))
    results = detect_outliers(events, ["price"], z_threshold=2.0)
    text = format_outliers(results)
    assert "price" in text


def test_format_outliers_reports_no_outliers():
    events = [_added({"price": str(i)}) for i in range(10)]
    results = detect_outliers(events, ["price"])
    text = format_outliers(results)
    assert "No outliers" in text
