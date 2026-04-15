"""Tests for csv_diff.baseline."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from csv_diff.baseline import (
    BaselineError,
    parse_baseline_path,
    save_baseline,
    load_baseline,
    diff_matches_baseline,
)
from csv_diff.diff import RowAdded, RowRemoved, RowModified


# ---------------------------------------------------------------------------
# parse_baseline_path
# ---------------------------------------------------------------------------

def test_parse_baseline_path_none_returns_none():
    assert parse_baseline_path(None) is None


def test_parse_baseline_path_returns_path_object():
    result = parse_baseline_path("snapshots/base.json")
    assert isinstance(result, Path)
    assert result == Path("snapshots/base.json")


# ---------------------------------------------------------------------------
# save_baseline / load_baseline round-trip
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_baseline(tmp_path):
    return tmp_path / "baseline.json"


def test_save_and_load_added_row(tmp_baseline):
    diff = [RowAdded(row={"id": "1", "name": "Alice"})]
    save_baseline(diff, tmp_baseline)
    loaded = load_baseline(tmp_baseline)
    assert len(loaded) == 1
    assert isinstance(loaded[0], RowAdded)
    assert loaded[0].row == {"id": "1", "name": "Alice"}


def test_save_and_load_removed_row(tmp_baseline):
    diff = [RowRemoved(row={"id": "2", "name": "Bob"})]
    save_baseline(diff, tmp_baseline)
    loaded = load_baseline(tmp_baseline)
    assert isinstance(loaded[0], RowRemoved)


def test_save_and_load_modified_row(tmp_baseline):
    diff = [RowModified(old_row={"id": "3", "val": "x"}, new_row={"id": "3", "val": "y"})]
    save_baseline(diff, tmp_baseline)
    loaded = load_baseline(tmp_baseline)
    assert isinstance(loaded[0], RowModified)
    assert loaded[0].new_row["val"] == "y"


def test_save_empty_diff(tmp_baseline):
    save_baseline([], tmp_baseline)
    loaded = load_baseline(tmp_baseline)
    assert loaded == []


def test_load_raises_when_file_missing(tmp_path):
    with pytest.raises(BaselineError, match="not found"):
        load_baseline(tmp_path / "no_such_file.json")


def test_load_raises_on_corrupt_json(tmp_baseline):
    tmp_baseline.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(BaselineError):
        load_baseline(tmp_baseline)


def test_load_raises_on_unknown_type(tmp_baseline):
    tmp_baseline.write_text(json.dumps([{"type": "upserted", "row": {}}]), encoding="utf-8")
    with pytest.raises(BaselineError, match="Unknown baseline event type"):
        load_baseline(tmp_baseline)


# ---------------------------------------------------------------------------
# diff_matches_baseline
# ---------------------------------------------------------------------------

def test_matches_identical_diffs():
    diff = [RowAdded(row={"id": "1"})]
    assert diff_matches_baseline(diff, diff) is True


def test_does_not_match_different_length():
    diff = [RowAdded(row={"id": "1"})]
    assert diff_matches_baseline(diff, []) is False


def test_does_not_match_different_content():
    a = [RowAdded(row={"id": "1"})]
    b = [RowAdded(row={"id": "2"})]
    assert diff_matches_baseline(a, b) is False
