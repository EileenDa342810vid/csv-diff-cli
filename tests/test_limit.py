"""Tests for csv_diff.limit."""
import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.limit import LimitError, limit_diff, parse_limit, was_truncated


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(key: str) -> RowAdded:
    return RowAdded(key=key, row={"id": key, "name": "x"})


def _removed(key: str) -> RowRemoved:
    return RowRemoved(key=key, row={"id": key, "name": "x"})


def _modified(key: str) -> RowModified:
    return RowModified(key=key, before={"id": key, "name": "a"}, after={"id": key, "name": "b"})


# ---------------------------------------------------------------------------
# parse_limit
# ---------------------------------------------------------------------------

def test_parse_limit_none_returns_none():
    assert parse_limit(None) is None


def test_parse_limit_integer_passthrough():
    assert parse_limit(5) == 5


def test_parse_limit_string_integer():
    assert parse_limit("10") == 10


def test_parse_limit_raises_on_non_integer():
    with pytest.raises(LimitError):
        parse_limit("abc")


def test_parse_limit_raises_on_zero():
    with pytest.raises(LimitError):
        parse_limit(0)


def test_parse_limit_raises_on_negative():
    with pytest.raises(LimitError):
        parse_limit(-3)


# ---------------------------------------------------------------------------
# limit_diff
# ---------------------------------------------------------------------------

def test_limit_diff_none_returns_all():
    events = [_added("1"), _removed("2"), _modified("3")]
    assert limit_diff(events, None) == events


def test_limit_diff_truncates_to_n():
    events = [_added(str(i)) for i in range(10)]
    result = limit_diff(events, 3)
    assert len(result) == 3
    assert result == events[:3]


def test_limit_diff_n_larger_than_list():
    events = [_added("1"), _added("2")]
    assert limit_diff(events, 100) == events


def test_limit_diff_empty_list():
    assert limit_diff([], 5) == []


# ---------------------------------------------------------------------------
# was_truncated
# ---------------------------------------------------------------------------

def test_was_truncated_false_when_no_limit():
    events = [_added(str(i)) for i in range(20)]
    assert was_truncated(events, None) is False


def test_was_truncated_true_when_over_limit():
    events = [_added(str(i)) for i in range(5)]
    assert was_truncated(events, 3) is True


def test_was_truncated_false_when_at_limit():
    events = [_added(str(i)) for i in range(3)]
    assert was_truncated(events, 3) is False
