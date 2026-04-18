"""Tests for csv_diff.checkpoint."""
import pytest
from pathlib import Path
from csv_diff.checkpoint import (
    CheckpointError,
    parse_checkpoint_name,
    save_checkpoint,
    load_checkpoint,
    compare_checkpoints,
    format_checkpoint,
)
from csv_diff.diff import RowAdded, RowRemoved, RowModified


def _added():
    return RowAdded(row={"id": "1", "name": "Alice"})


def _removed():
    return RowRemoved(row={"id": "2", "name": "Bob"})


def _modified():
    return RowModified(
        key="3",
        before={"id": "3", "name": "Old"},
        after={"id": "3", "name": "New"},
    )


def test_parse_checkpoint_name_none_returns_none():
    assert parse_checkpoint_name(None) is None


def test_parse_checkpoint_name_empty_returns_none():
    assert parse_checkpoint_name("   ") is None


def test_parse_checkpoint_name_strips_whitespace():
    assert parse_checkpoint_name("  v1  ") == "v1"


def test_save_and_load_round_trip(tmp_path):
    events = [_added(), _removed(), _modified()]
    meta = save_checkpoint("v1", events, tmp_path)
    assert meta.added == 1
    assert meta.removed == 1
    assert meta.modified == 1
    loaded = load_checkpoint(meta.path)
    assert loaded.name == "v1"
    assert loaded.added == 1
    assert loaded.removed == 1
    assert loaded.modified == 1


def test_save_creates_file(tmp_path):
    save_checkpoint("snap", [], tmp_path)
    assert (tmp_path / "snap.json").exists()


def test_save_spaces_in_name_uses_underscores(tmp_path):
    meta = save_checkpoint("my snap", [], tmp_path)
    assert meta.path.name == "my_snap.json"


def test_load_raises_on_missing_file(tmp_path):
    with pytest.raises(CheckpointError, match="not found"):
        load_checkpoint(tmp_path / "nope.json")


def test_load_raises_on_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(CheckpointError, match="Invalid"):
        load_checkpoint(bad)


def test_compare_checkpoints_shows_delta(tmp_path):
    a = save_checkpoint("a", [_added()], tmp_path / "a")
    b = save_checkpoint("b", [_added(), _added(), _removed()], tmp_path / "b")
    lines = compare_checkpoints(a, b)
    assert any("added" in l and "+1" in l for l in lines)
    assert any("removed" in l and "+1" in l for l in lines)


def test_format_checkpoint_contains_name(tmp_path):
    meta = save_checkpoint("release", [_modified()], tmp_path)
    out = format_checkpoint(meta)
    assert "release" in out
    assert "modified:  1" in out
