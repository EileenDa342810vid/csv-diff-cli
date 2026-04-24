"""Tests for csv_diff.supersede."""
from __future__ import annotations

from pathlib import Path

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.supersede import (
    SupersedeError,
    SupersedeResult,
    apply_supersede,
    load_supersede_keys,
    parse_supersede_path,
    save_supersede_keys,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(key, **extra):
    return RowAdded(row={"id": key, **extra})


def _removed(key, **extra):
    return RowRemoved(row={"id": key, **extra})


def _modified(key, **extra):
    return RowModified(old_row={"id": key, **extra}, new_row={"id": key, **extra})


# ---------------------------------------------------------------------------
# parse_supersede_path
# ---------------------------------------------------------------------------

def test_parse_supersede_path_none_returns_none():
    assert parse_supersede_path(None) is None


def test_parse_supersede_path_empty_returns_none():
    assert parse_supersede_path("") is None


def test_parse_supersede_path_returns_path():
    result = parse_supersede_path("/tmp/keys.txt")
    assert isinstance(result, Path)
    assert str(result) == "/tmp/keys.txt"


# ---------------------------------------------------------------------------
# load_supersede_keys
# ---------------------------------------------------------------------------

def test_load_supersede_keys_reads_lines(tmp_path):
    f = tmp_path / "keys.txt"
    f.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    keys = load_supersede_keys(f)
    assert keys == {"alpha", "beta", "gamma"}


def test_load_supersede_keys_ignores_blank_lines(tmp_path):
    f = tmp_path / "keys.txt"
    f.write_text("alpha\n\nbeta\n", encoding="utf-8")
    keys = load_supersede_keys(f)
    assert keys == {"alpha", "beta"}


def test_load_supersede_keys_raises_on_missing_file(tmp_path):
    with pytest.raises(SupersedeError):
        load_supersede_keys(tmp_path / "nonexistent.txt")


# ---------------------------------------------------------------------------
# save_supersede_keys
# ---------------------------------------------------------------------------

def test_save_supersede_keys_round_trip(tmp_path):
    f = tmp_path / "keys.txt"
    events = [_added("1"), _removed("2"), _modified("3")]
    save_supersede_keys(f, events)
    keys = load_supersede_keys(f)
    assert keys == {"1", "2", "3"}


def test_save_supersede_keys_empty_events(tmp_path):
    f = tmp_path / "keys.txt"
    save_supersede_keys(f, [])
    assert f.read_text(encoding="utf-8") == ""


# ---------------------------------------------------------------------------
# apply_supersede
# ---------------------------------------------------------------------------

def test_apply_supersede_empty_known_keeps_all():
    events = [_added("1"), _removed("2")]
    result = apply_supersede(events, set())
    assert result.kept == events
    assert result.dropped == 0


def test_apply_supersede_drops_known_keys():
    events = [_added("1"), _added("2"), _removed("3")]
    result = apply_supersede(events, {"2"})
    assert len(result.kept) == 2
    assert result.dropped == 1
    assert all(_added("2") != e for e in result.kept)


def test_apply_supersede_drops_all_when_all_known():
    events = [_added("1"), _modified("2")]
    result = apply_supersede(events, {"1", "2"})
    assert result.kept == []
    assert result.dropped == 2


def test_apply_supersede_returns_supersede_result():
    result = apply_supersede([], set())
    assert isinstance(result, SupersedeResult)
