"""Unit tests for csv_diff.correlation."""
from __future__ import annotations

import pytest

from csv_diff.correlation import (
    ColumnPair,
    CorrelationError,
    CorrelationResult,
    compute_correlation,
    format_correlation,
    parse_correlation_columns,
    validate_correlation_columns,
)


def _modified(changes: dict):
    from csv_diff.diff import RowModified
    return RowModified(key="k1", changes=changes)


def _added():
    from csv_diff.diff import RowAdded
    return RowAdded(key="k2", row={"a": "1"})


# --- parse_correlation_columns ---

def test_parse_correlation_columns_none_returns_none():
    assert parse_correlation_columns(None) is None


def test_parse_correlation_columns_empty_returns_none():
    assert parse_correlation_columns("") is None


def test_parse_correlation_columns_single():
    assert parse_correlation_columns("price") == ["price"]


def test_parse_correlation_columns_multiple():
    assert parse_correlation_columns("price, qty") == ["price", "qty"]


def test_parse_correlation_columns_raises_on_empty_entry():
    with pytest.raises(CorrelationError):
        parse_correlation_columns("price,,qty")


# --- validate_correlation_columns ---

def test_validate_columns_passes_when_present():
    validate_correlation_columns(["a", "b"], ["a", "b", "c"])  # no exception


def test_validate_columns_raises_on_unknown():
    with pytest.raises(CorrelationError, match="Unknown"):
        validate_correlation_columns(["x"], ["a", "b"])


# --- compute_correlation ---

def test_empty_diff_returns_empty_result():
    result = compute_correlation([])
    assert result.total_modified == 0
    assert result.pairs == {}


def test_added_row_not_counted():
    result = compute_correlation([_added()])
    assert result.total_modified == 0


def test_single_column_change_no_pairs():
    event = _modified({"price": ("10", "20")})
    result = compute_correlation([event])
    assert result.total_modified == 1
    assert result.pairs == {}


def test_two_column_changes_creates_pair():
    event = _modified({"price": ("10", "20"), "qty": ("1", "2")})
    result = compute_correlation([event])
    assert len(result.pairs) == 1
    pair = next(iter(result.pairs.values()))
    assert pair.co_changes == 1


def test_pair_key_is_alphabetical():
    event = _modified({"zzz": ("a", "b"), "aaa": ("x", "y")})
    result = compute_correlation([event])
    key = next(iter(result.pairs))
    assert key == ("aaa", "zzz")


def test_multiple_events_accumulate():
    e1 = _modified({"price": ("1", "2"), "qty": ("1", "2")})
    e2 = _modified({"price": ("2", "3"), "qty": ("2", "3")})
    result = compute_correlation([e1, e2])
    pair = result.pairs[("price", "qty")]
    assert pair.co_changes == 2


def test_column_filter_excludes_irrelevant():
    event = _modified({"price": ("1", "2"), "qty": ("1", "2"), "name": ("a", "b")})
    result = compute_correlation([event], columns=["price", "qty"])
    assert ("name", "price") not in result.pairs
    assert ("name", "qty") not in result.pairs


# --- format_correlation ---

def test_format_correlation_no_pairs():
    result = CorrelationResult()
    text = format_correlation(result)
    assert "No co-changing" in text


def test_format_correlation_shows_pair():
    result = CorrelationResult(total_modified=1)
    result.pairs[("price", "qty")] = ColumnPair(col_a="price", col_b="qty", co_changes=3)
    text = format_correlation(result)
    assert "price" in text
    assert "qty" in text
    assert "3" in text
