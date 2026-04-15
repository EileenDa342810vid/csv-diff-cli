"""Tests for csv_diff.truncate."""

import pytest

from csv_diff.truncate import (
    TruncateError,
    parse_max_width,
    truncate_value,
    truncate_row,
    DEFAULT_MAX_WIDTH,
)


# ---------------------------------------------------------------------------
# parse_max_width
# ---------------------------------------------------------------------------

def test_parse_max_width_none_returns_none():
    assert parse_max_width(None) is None


def test_parse_max_width_integer_passthrough():
    assert parse_max_width(20) == 20


def test_parse_max_width_string_integer():
    assert parse_max_width("30") == 30


def test_parse_max_width_raises_on_non_integer():
    with pytest.raises(TruncateError, match="must be an integer"):
        parse_max_width("abc")


def test_parse_max_width_raises_on_zero():
    with pytest.raises(TruncateError, match="positive integer"):
        parse_max_width(0)


def test_parse_max_width_raises_on_negative():
    with pytest.raises(TruncateError, match="positive integer"):
        parse_max_width(-5)


def test_default_max_width_is_positive():
    assert DEFAULT_MAX_WIDTH > 0


# ---------------------------------------------------------------------------
# truncate_value
# ---------------------------------------------------------------------------

def test_truncate_value_none_max_width_returns_unchanged():
    assert truncate_value("hello world", None) == "hello world"


def test_truncate_value_short_string_unchanged():
    assert truncate_value("hi", 10) == "hi"


def test_truncate_value_exact_length_unchanged():
    assert truncate_value("hello", 5) == "hello"


def test_truncate_value_long_string_truncated():
    result = truncate_value("abcdefghij", 7)
    assert result == "abcd..."
    assert len(result) == 7


def test_truncate_value_very_small_max_width():
    result = truncate_value("hello", 3)
    assert len(result) <= 3


def test_truncate_value_result_never_exceeds_max_width():
    for width in range(1, 15):
        result = truncate_value("a" * 20, width)
        assert len(result) <= width


# ---------------------------------------------------------------------------
# truncate_row
# ---------------------------------------------------------------------------

def test_truncate_row_none_max_width_returns_same_dict():
    row = {"a": "hello", "b": "world"}
    assert truncate_row(row, None) == row


def test_truncate_row_truncates_long_values():
    row = {"name": "Alexander Hamilton", "city": "NYC"}
    result = truncate_row(row, 10)
    assert len(result["name"]) <= 10
    assert result["city"] == "NYC"


def test_truncate_row_does_not_mutate_original():
    row = {"x": "a" * 50}
    original_val = row["x"]
    truncate_row(row, 10)
    assert row["x"] == original_val
