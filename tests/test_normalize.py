"""Tests for csv_diff.normalize."""

import pytest

from csv_diff.normalize import (
    NormalizeError,
    apply_normalizers,
    normalize_row,
    normalize_rows,
    parse_normalizers,
)


def test_parse_normalizers_none_returns_none():
    assert parse_normalizers(None) is None


def test_parse_normalizers_empty_string_returns_none():
    assert parse_normalizers("") is None
    assert parse_normalizers("   ") is None


def test_parse_normalizers_single():
    assert parse_normalizers("strip") == ["strip"]


def test_parse_normalizers_multiple():
    assert parse_normalizers("strip,lower") == ["strip", "lower"]


def test_parse_normalizers_strips_whitespace():
    assert parse_normalizers(" strip , upper ") == ["strip", "upper"]


def test_parse_normalizers_raises_on_unknown():
    with pytest.raises(NormalizeError, match="Unknown normalizer"):
        parse_normalizers("strip,bogus")


def test_parse_normalizers_raises_on_empty_entry():
    with pytest.raises(NormalizeError, match="Empty normalizer"):
        parse_normalizers("strip,,lower")


def test_apply_normalizers_strip():
    assert apply_normalizers("  hello  ", ["strip"]) == "hello"


def test_apply_normalizers_lower():
    assert apply_normalizers("HELLO", ["lower"]) == "hello"


def test_apply_normalizers_upper():
    assert apply_normalizers("hello", ["upper"]) == "HELLO"


def test_apply_normalizers_chained():
    assert apply_normalizers("  HELLO  ", ["strip", "lower"]) == "hello"


def test_apply_normalizers_raises_on_unknown():
    with pytest.raises(NormalizeError):
        apply_normalizers("x", ["bad"])


def test_normalize_row_applies_to_all_columns():
    row = {"name": "  Alice  ", "city": "  NYC  "}
    result = normalize_row(row, ["strip"])
    assert result == {"name": "Alice", "city": "NYC"}


def test_normalize_rows_returns_original_when_none():
    rows = [{"a": "  X  "}]
    assert normalize_rows(rows, None) is rows


def test_normalize_rows_transforms_all():
    rows = [{"a": "  Hello "}, {"a": " World  "}]
    result = normalize_rows(rows, ["strip", "lower"])
    assert result == [{"a": "hello"}, {"a": "world"}]
