"""Tests for csv_diff.split."""
import pytest
from csv_diff.split import SplitError, SplitResult, split_diff, format_split
from csv_diff.diff import RowAdded, RowRemoved, RowModified


def _added():
    return RowAdded(row={"id": "1", "name": "Alice"})


def _removed():
    return RowRemoved(row={"id": "2", "name": "Bob"})


def _modified():
    return RowModified(
        key="3",
        before={"id": "3", "name": "Carol"},
        after={"id": "3", "name": "Caroline"},
    )


def test_empty_diff_returns_empty_result():
    r = split_diff([])
    assert r.added == []
    assert r.removed == []
    assert r.modified == []
    assert r.total == 0


def test_split_added():
    r = split_diff([_added()])
    assert len(r.added) == 1
    assert r.removed == []
    assert r.modified == []


def test_split_removed():
    r = split_diff([_removed()])
    assert r.added == []
    assert len(r.removed) == 1


def test_split_modified():
    r = split_diff([_modified()])
    assert len(r.modified) == 1


def test_split_mixed():
    events = [_added(), _removed(), _modified(), _added()]
    r = split_diff(events)
    assert len(r.added) == 2
    assert len(r.removed) == 1
    assert len(r.modified) == 1
    assert r.total == 4


def test_split_raises_on_unknown_event():
    with pytest.raises(SplitError):
        split_diff([object()])


def test_split_error_message_contains_type():
    """SplitError should mention the unexpected type to aid debugging."""
    class Unexpected:
        pass

    with pytest.raises(SplitError, match="Unexpected"):
        split_diff([Unexpected()])


def test_format_split_contains_headers():
    r = split_diff([_added(), _modified()])
    out = format_split(r)
    assert "Added" in out
    assert "Removed" in out
    assert "Modified" in out
    assert "Total" in out


def test_format_split_counts_correct():
    r = split_diff([_added(), _added(), _removed()])
    out = format_split(r)
    assert "2" in out
    assert "1" in out
