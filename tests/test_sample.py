"""Tests for csv_diff.sample."""

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.sample import SampleError, parse_sample_size, sample_diff


def _added(key: str) -> RowAdded:
    return RowAdded(key=key, row={"id": key, "name": "x"})


def _removed(key: str) -> RowRemoved:
    return RowRemoved(key=key, row={"id": key, "name": "x"})


def _modified(key: str) -> RowModified:
    return RowModified(key=key, before={"id": key, "name": "a"}, after={"id": key, "name": "b"})


EVENTS = [_added("1"), _removed("2"), _modified("3"), _added("4"), _removed("5")]


def test_parse_sample_size_none_returns_none():
    assert parse_sample_size(None) is None


def test_parse_sample_size_integer_passthrough():
    assert parse_sample_size(10) == 10


def test_parse_sample_size_string_integer():
    assert parse_sample_size("3") == 3


def test_parse_sample_size_raises_on_non_integer():
    with pytest.raises(SampleError):
        parse_sample_size("abc")


def test_parse_sample_size_raises_on_zero():
    with pytest.raises(SampleError):
        parse_sample_size(0)


def test_parse_sample_size_raises_on_negative():
    with pytest.raises(SampleError):
        parse_sample_size(-1)


def test_sample_none_returns_all():
    assert sample_diff(EVENTS, None) == EVENTS


def test_sample_head_limits_count():
    result = sample_diff(EVENTS, 3, mode="head")
    assert result == EVENTS[:3]


def test_sample_head_larger_than_list_returns_all():
    result = sample_diff(EVENTS, 100, mode="head")
    assert result == EVENTS


def test_sample_random_returns_correct_count():
    result = sample_diff(EVENTS, 3, mode="random", seed=42)
    assert len(result) == 3


def test_sample_random_elements_are_subset():
    result = sample_diff(EVENTS, 4, mode="random", seed=7)
    for event in result:
        assert event in EVENTS


def test_sample_random_larger_than_list_returns_all():
    result = sample_diff(EVENTS, 100, mode="random", seed=0)
    assert len(result) == len(EVENTS)


def test_sample_unknown_mode_raises():
    with pytest.raises(SampleError, match="Unknown sample mode"):
        sample_diff(EVENTS, 2, mode="tail")
