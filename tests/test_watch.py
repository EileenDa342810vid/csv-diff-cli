"""Tests for csv_diff.watch."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from csv_diff.watch import (
    WatchError,
    WatchState,
    parse_interval,
    watch,
)


# ---------------------------------------------------------------------------
# parse_interval
# ---------------------------------------------------------------------------

def test_parse_interval_none_returns_default():
    assert parse_interval(None) == 2.0


def test_parse_interval_float_passthrough():
    assert parse_interval(0.5) == 0.5


def test_parse_interval_string_integer():
    assert parse_interval("3") == 3.0


def test_parse_interval_raises_on_non_numeric():
    with pytest.raises(WatchError, match="number"):
        parse_interval("fast")


def test_parse_interval_raises_on_zero():
    with pytest.raises(WatchError, match="positive"):
        parse_interval(0)


def test_parse_interval_raises_on_negative():
    with pytest.raises(WatchError, match="positive"):
        parse_interval(-1)


# ---------------------------------------------------------------------------
# WatchState
# ---------------------------------------------------------------------------

def test_watch_state_detects_modification(tmp_path: Path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name\n1,Alice\n")
    b.write_text("id,name\n1,Alice\n")

    state = WatchState(path_a=a, path_b=b)
    state.changed()  # prime

    # Modify file a
    time.sleep(0.05)
    a.write_text("id,name\n2,Bob\n")
    assert state.changed() is True


def test_watch_state_no_change_returns_false(tmp_path: Path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id\n1\n")
    b.write_text("id\n1\n")

    state = WatchState(path_a=a, path_b=b)
    state.changed()  # prime
    assert state.changed() is False


# ---------------------------------------------------------------------------
# watch()
# ---------------------------------------------------------------------------

def test_watch_raises_on_missing_file_a(tmp_path: Path):
    b = tmp_path / "b.csv"
    b.write_text("id\n1\n")
    with pytest.raises(WatchError, match="File not found"):
        watch(tmp_path / "missing.csv", b, callback=lambda: None, max_iterations=1)


def test_watch_raises_on_missing_file_b(tmp_path: Path):
    a = tmp_path / "a.csv"
    a.write_text("id\n1\n")
    with pytest.raises(WatchError, match="File not found"):
        watch(a, tmp_path / "missing.csv", callback=lambda: None, max_iterations=1)


def test_watch_calls_callback_on_change(tmp_path: Path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id\n1\n")
    b.write_text("id\n1\n")

    calls: list[int] = []

    def _on_change() -> None:
        calls.append(1)
        # Restore so subsequent polls don't fire again
        a.write_text("id\n1\n")

    # Modify a before the second iteration fires
    state = WatchState(path_a=a, path_b=b)
    state.changed()  # prime internal mtimes

    time.sleep(0.05)
    a.write_text("id\n2\n")

    watch(a, b, callback=_on_change, interval=0.01, max_iterations=2)
    assert len(calls) >= 1
