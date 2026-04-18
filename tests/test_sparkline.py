"""Tests for csv_diff.sparkline."""
import pytest
from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.sparkline import (
    SparklineError,
    SparklineResult,
    _extract_values,
    _render,
    compute_sparkline,
    format_sparkline,
    parse_sparkline_column,
)


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(key="k", old_row=old, new_row=new)


def test_parse_sparkline_column_none_returns_none():
    assert parse_sparkline_column(None) is None


def test_parse_sparkline_column_empty_returns_none():
    assert parse_sparkline_column("  ") is None


def test_parse_sparkline_column_strips_whitespace():
    assert parse_sparkline_column("  price  ") == "price"


def test_extract_values_from_added():
    events = [_added({"price": "10"}), _added({"price": "20"})]
    assert _extract_values(events, "price") == [10.0, 20.0]


def test_extract_values_from_removed():
    events = [_removed({"price": "5"})]
    assert _extract_values(events, "price") == [5.0]


def test_extract_values_from_modified_uses_new_row():
    events = [_modified({"price": "1"}, {"price": "99"})]
    assert _extract_values(events, "price") == [99.0]


def test_extract_values_skips_non_numeric():
    events = [_added({"price": "abc"}), _added({"price": "7"})]
    assert _extract_values(events, "price") == [7.0]


def test_extract_values_skips_missing_column():
    events = [_added({"other": "3"})]
    assert _extract_values(events, "price") == []


def test_render_single_value_uses_max_char():
    result = _render([5.0])
    assert len(result) == 1


def test_render_ascending_sequence():
    line = _render([0.0, 1.0, 2.0, 3.0])
    assert len(line) == 4
    # characters should be non-decreasing
    for a, b in zip(line, line[1:]):
        assert a <= b


def test_render_empty_returns_empty_string():
    assert _render([]) == ""


def test_compute_sparkline_returns_result():
    events = [_added({"v": str(i)}) for i in range(5)]
    result = compute_sparkline(events, "v")
    assert isinstance(result, SparklineResult)
    assert result.column == "v"
    assert len(result.values) == 5


def test_compute_sparkline_raises_on_no_data():
    with pytest.raises(SparklineError):
        compute_sparkline([], "price")


def test_format_sparkline_contains_column_name():
    events = [_added({"score": "42"})]
    result = compute_sparkline(events, "score")
    text = format_sparkline(result)
    assert "score" in text
    assert "n=1" in text
