"""Unit tests for csv_diff.interpolate."""
import pytest

from csv_diff.interpolate import (
    InterpolateError,
    interpolate_row,
    interpolate_rows,
    parse_fill_value,
    parse_interpolate_columns,
    validate_interpolate_columns,
)


def test_parse_interpolate_columns_none_returns_none():
    assert parse_interpolate_columns(None) is None


def test_parse_interpolate_columns_empty_string_returns_none():
    assert parse_interpolate_columns("") is None


def test_parse_interpolate_columns_single():
    assert parse_interpolate_columns("price") == ["price"]


def test_parse_interpolate_columns_multiple():
    assert parse_interpolate_columns("price, qty") == ["price", "qty"]


def test_parse_interpolate_columns_raises_on_empty_entry():
    with pytest.raises(InterpolateError):
        parse_interpolate_columns("price,,qty")


def test_parse_fill_value_none_returns_zero():
    assert parse_fill_value(None) == 0.0


def test_parse_fill_value_integer_string():
    assert parse_fill_value("5") == 5.0


def test_parse_fill_value_float_string():
    assert parse_fill_value("3.14") == pytest.approx(3.14)


def test_parse_fill_value_raises_on_non_numeric():
    with pytest.raises(InterpolateError):
        parse_fill_value("abc")


def test_validate_interpolate_columns_all_present():
    validate_interpolate_columns(["a", "b"], ["a", "b", "c"])  # no exception


def test_validate_interpolate_columns_raises_on_missing():
    with pytest.raises(InterpolateError, match="not found"):
        validate_interpolate_columns(["a", "z"], ["a", "b"])


def test_interpolate_row_fills_blank():
    row = {"name": "Alice", "score": ""}
    result = interpolate_row(row, ["score"], 0.0)
    assert result["score"] == "0.0"


def test_interpolate_row_leaves_non_blank_unchanged():
    row = {"name": "Alice", "score": "42"}
    result = interpolate_row(row, ["score"], 0.0)
    assert result["score"] == "42"


def test_interpolate_row_fills_whitespace_only():
    row = {"val": "   "}
    result = interpolate_row(row, ["val"], -1.0)
    assert result["val"] == "-1.0"


def test_interpolate_row_does_not_mutate_original():
    row = {"val": ""}
    _ = interpolate_row(row, ["val"], 99.0)
    assert row["val"] == ""


def test_interpolate_rows_applies_to_all():
    rows = [{"x": ""}, {"x": "1"}, {"x": ""}]
    result = interpolate_rows(rows, ["x"], 7.0)
    assert result[0]["x"] == "7.0"
    assert result[1]["x"] == "1"
    assert result[2]["x"] == "7.0"
