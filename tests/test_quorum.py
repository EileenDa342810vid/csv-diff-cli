"""Tests for csv_diff.quorum."""

from __future__ import annotations

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.quorum import (
    QuorumError,
    format_quorum,
    parse_quorum,
    quorum_diff,
)


def _added(row: dict) -> RowAdded:
    return RowAdded(row=row)


def _removed(row: dict) -> RowRemoved:
    return RowRemoved(row=row)


def _modified(old: dict, new: dict) -> RowModified:
    return RowModified(old_row=old, new_row=new)


# ---------------------------------------------------------------------------
# parse_quorum
# ---------------------------------------------------------------------------

def test_parse_quorum_none_returns_none():
    assert parse_quorum(None) is None


def test_parse_quorum_integer_passthrough():
    assert parse_quorum(3) == 3


def test_parse_quorum_string_integer():
    assert parse_quorum("2") == 2


def test_parse_quorum_raises_on_non_integer():
    with pytest.raises(QuorumError):
        parse_quorum("half")


def test_parse_quorum_raises_on_zero():
    with pytest.raises(QuorumError):
        parse_quorum(0)


def test_parse_quorum_raises_on_negative():
    with pytest.raises(QuorumError):
        parse_quorum(-1)


# ---------------------------------------------------------------------------
# quorum_diff
# ---------------------------------------------------------------------------

def test_empty_diff_lists_returns_empty():
    result = quorum_diff([], quorum=1)
    assert result.events == []
    assert result.accepted == 0


def test_single_source_quorum_1_passes_all():
    events = [_added({"id": "1"}), _removed({"id": "2"})]
    result = quorum_diff([events], quorum=1)
    assert result.accepted == 2


def test_two_sources_quorum_2_keeps_intersection():
    e1 = _added({"id": "1"})
    e2 = _added({"id": "2"})
    result = quorum_diff([[e1, e2], [e1]], quorum=2)
    assert result.accepted == 1
    assert result.events[0] is e1


def test_two_sources_quorum_1_keeps_union():
    e1 = _added({"id": "1"})
    e2 = _added({"id": "2"})
    result = quorum_diff([[e1], [e2]], quorum=1)
    assert result.accepted == 2


def test_rejected_count_is_correct():
    e1 = _added({"id": "1"})
    e2 = _added({"id": "2"})
    result = quorum_diff([[e1, e2], [e1]], quorum=2)
    # total_candidates = 3, accepted = 1
    assert result.rejected == 2


def test_quorum_raises_on_invalid_threshold():
    with pytest.raises(QuorumError):
        quorum_diff([[]], quorum=0)


def test_modified_events_are_matched():
    e = _modified({"id": "1", "v": "a"}, {"id": "1", "v": "b"})
    result = quorum_diff([[e], [e]], quorum=2)
    assert result.accepted == 1


# ---------------------------------------------------------------------------
# format_quorum
# ---------------------------------------------------------------------------

def test_format_quorum_contains_header():
    result = quorum_diff([], quorum=2)
    text = format_quorum(result)
    assert "Quorum Report" in text


def test_format_quorum_shows_required():
    result = quorum_diff([], quorum=3)
    text = format_quorum(result)
    assert "3" in text
