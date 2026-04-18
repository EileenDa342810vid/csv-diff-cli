"""Tests for csv_diff.slice."""

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.slice import (
    SliceConfig,
    SliceError,
    describe_slice,
    parse_slice,
    slice_diff,
)


def _added(key: str) -> RowAdded:
    return RowAdded(key=key, row={"id": key})


def _removed(key: str) -> RowRemoved:
    return RowRemoved(key=key, row={"id": key})


def _modified(key: str) -> RowModified:
    return RowModified(key=key, old_row={"id": key, "v": "1"}, new_row={"id": key, "v": "2"})


EVENTS = [_added("a"), _removed("b"), _modified("c"), _added("d"), _removed("e")]


def test_parse_slice_none_returns_none():
    assert parse_slice(None) is None


def test_parse_slice_empty_returns_none():
    assert parse_slice("") is None


def test_parse_slice_stop_only():
    cfg = parse_slice("3")
    assert cfg == SliceConfig(start=0, stop=3)


def test_parse_slice_start_and_stop():
    cfg = parse_slice("2:5")
    assert cfg == SliceConfig(start=2, stop=5)


def test_parse_slice_open_stop():
    cfg = parse_slice("2:")
    assert cfg == SliceConfig(start=2, stop=None)


def test_parse_slice_open_start():
    cfg = parse_slice(":4")
    assert cfg == SliceConfig(start=0, stop=4)


def test_parse_slice_raises_on_negative_start():
    with pytest.raises(SliceError):
        parse_slice("-1:5")


def test_parse_slice_raises_when_stop_not_greater_than_start():
    with pytest.raises(SliceError):
        parse_slice("5:3")


def test_slice_diff_none_returns_all():
    assert slice_diff(EVENTS, None) == EVENTS


def test_slice_diff_stop_only():
    result = slice_diff(EVENTS, SliceConfig(start=0, stop=2))
    assert result == EVENTS[:2]


def test_slice_diff_start_and_stop():
    result = slice_diff(EVENTS, SliceConfig(start=1, stop=4))
    assert result == EVENTS[1:4]


def test_slice_diff_open_stop():
    result = slice_diff(EVENTS, SliceConfig(start=2, stop=None))
    assert result == EVENTS[2:]


def test_describe_slice_bounded():
    cfg = SliceConfig(start=0, stop=3)
    desc = describe_slice(cfg, 5)
    assert "0" in desc and "3" in desc and "5" in desc


def test_describe_slice_unbounded_uses_total():
    cfg = SliceConfig(start=1, stop=None)
    desc = describe_slice(cfg, 4)
    assert "4" in desc
