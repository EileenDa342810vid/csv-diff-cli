"""Tests for csv_diff.bucket."""
import pytest

from csv_diff.bucket import (
    BucketError,
    BucketResult,
    bucket_diff,
    format_bucket_table,
    parse_bucket_column,
    parse_bucket_edges,
)
from csv_diff.diff import RowAdded, RowModified, RowRemoved


def _added(row): return RowAdded(row=row)
def _removed(row): return RowRemoved(row=row)
def _modified(old, new): return RowModified(key="k", old_row=old, new_row=new)


def test_parse_bucket_column_none_returns_none():
    assert parse_bucket_column(None) is None


def test_parse_bucket_column_strips_whitespace():
    assert parse_bucket_column("  amount  ") == "amount"


def test_parse_bucket_edges_valid():
    assert parse_bucket_edges("0,100,500") == [0.0, 100.0, 500.0]


def test_parse_bucket_edges_none_returns_none():
    assert parse_bucket_edges(None) is None


def test_parse_bucket_edges_raises_on_non_numeric():
    with pytest.raises(BucketError):
        parse_bucket_edges("0,abc,500")


def test_parse_bucket_edges_raises_on_unsorted():
    with pytest.raises(BucketError):
        parse_bucket_edges("500,100,0")


def test_bucket_diff_counts_added():
    events = [_added({"amount": "50"})]
    result = bucket_diff(events, "amount", [0.0, 100.0, 500.0])
    assert result["0.0-100.0"].added == 1


def test_bucket_diff_counts_removed():
    events = [_removed({"amount": "200"})]
    result = bucket_diff(events, "amount", [0.0, 100.0, 500.0])
    assert result["100.0-500.0"].removed == 1


def test_bucket_diff_counts_modified_uses_new_row():
    events = [_modified({"amount": "50"}, {"amount": "600"})]
    result = bucket_diff(events, "amount", [0.0, 100.0, 500.0])
    assert result[">= 500.0"].modified == 1 or result[">=500.0"].modified == 1


def test_bucket_diff_non_numeric_goes_to_other():
    events = [_added({"amount": "n/a"})]
    result = bucket_diff(events, "amount", [0.0, 100.0])
    assert result["other"].added == 1


def test_bucket_diff_raises_on_missing_column():
    events = [_added({"price": "10"})]
    with pytest.raises(BucketError):
        bucket_diff(events, "amount", [0.0, 100.0])


def test_format_bucket_table_empty():
    assert "No bucketed" in format_bucket_table({})


def test_format_bucket_table_contains_bucket_name():
    buckets = {"0.0-100.0": BucketResult(name="0.0-100.0", added=3)}
    out = format_bucket_table(buckets)
    assert "0.0-100.0" in out
    assert "3" in out
