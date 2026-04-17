"""Tests for csv_diff.timetravel snapshot save/load."""

import pytest
from pathlib import Path

from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.timetravel import (
    TimeTravelError,
    parse_snapshot_path,
    save_snapshot,
    load_snapshot,
    format_snapshot_header,
)


@pytest.fixture()
def tmp_snap(tmp_path):
    return tmp_path / "snap.json"


def test_parse_snapshot_path_none_returns_none():
    assert parse_snapshot_path(None) is None


def test_parse_snapshot_path_empty_returns_none():
    assert parse_snapshot_path("") is None


def test_parse_snapshot_path_returns_path(tmp_path):
    p = str(tmp_path / "snap.json")
    result = parse_snapshot_path(p)
    assert isinstance(result, Path)
    assert result == Path(p)


def test_save_and_load_round_trip(tmp_snap):
    events = [
        RowAdded(row={"id": "1", "name": "Alice"}),
        RowRemoved(row={"id": "2", "name": "Bob"}),
    ]
    save_snapshot(events, tmp_snap)
    ts, loaded = load_snapshot(tmp_snap)
    assert ts.endswith("Z")
    assert len(loaded) == 2
    assert isinstance(loaded[0], RowAdded)
    assert loaded[0].row["name"] == "Alice"
    assert isinstance(loaded[1], RowRemoved)


def test_save_and_load_modified(tmp_snap):
    events = [RowModified(key="3", before={"id": "3", "v": "old"}, after={"id": "3", "v": "new"})]
    save_snapshot(events, tmp_snap)
    _, loaded = load_snapshot(tmp_snap)
    assert isinstance(loaded[0], RowModified)
    assert loaded[0].after["v"] == "new"


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(TimeTravelError, match="not found"):
        load_snapshot(tmp_path / "missing.json")


def test_load_corrupt_file_raises(tmp_snap):
    tmp_snap.write_text("not json")
    with pytest.raises(TimeTravelError, match="Cannot read snapshot"):
        load_snapshot(tmp_snap)


def test_format_snapshot_header_contains_filename(tmp_snap):
    header = format_snapshot_header("2024-01-01T00:00:00Z", tmp_snap)
    assert "snap.json" in header
    assert "2024-01-01" in header
