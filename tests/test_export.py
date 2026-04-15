"""Tests for csv_diff.export."""
import json
import pytest

from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.export import (
    ExportError,
    parse_export_format,
    export_json,
    export_markdown,
    export_diff,
)
from csv_diff.stats import DiffStats


# ---------------------------------------------------------------------------
# parse_export_format
# ---------------------------------------------------------------------------

def test_parse_export_format_none_returns_none():
    assert parse_export_format(None) is None


def test_parse_export_format_json():
    assert parse_export_format("json") == "json"


def test_parse_export_format_markdown():
    assert parse_export_format("markdown") == "markdown"


def test_parse_export_format_case_insensitive():
    assert parse_export_format("JSON") == "json"
    assert parse_export_format("Markdown") == "markdown"


def test_parse_export_format_raises_on_unknown():
    with pytest.raises(ExportError, match="Unknown export format"):
        parse_export_format("xml")


# ---------------------------------------------------------------------------
# export_json
# ---------------------------------------------------------------------------

def test_export_json_added_row():
    changes = [RowAdded(row={"id": "1", "name": "Alice"})]
    result = json.loads(export_json(changes))
    assert result["changes"][0]["type"] == "added"
    assert result["changes"][0]["row"]["name"] == "Alice"


def test_export_json_removed_row():
    changes = [RowRemoved(row={"id": "2", "name": "Bob"})]
    result = json.loads(export_json(changes))
    assert result["changes"][0]["type"] == "removed"


def test_export_json_modified_row():
    changes = [RowModified(key="3", before={"id": "3", "val": "old"}, after={"id": "3", "val": "new"})]
    result = json.loads(export_json(changes))
    assert result["changes"][0]["type"] == "modified"
    assert result["changes"][0]["before"]["val"] == "old"


def test_export_json_includes_stats():
    stats = DiffStats(added=1, removed=0, modified=2, unchanged=5)
    result = json.loads(export_json([], stats=stats))
    assert result["stats"]["added"] == 1
    assert result["stats"]["modified"] == 2


def test_export_json_empty_changes():
    result = json.loads(export_json([]))
    assert result["changes"] == []


# ---------------------------------------------------------------------------
# export_markdown
# ---------------------------------------------------------------------------

def test_export_markdown_no_changes():
    assert export_markdown([]) == "_No differences found._"


def test_export_markdown_added_row_contains_plus():
    changes = [RowAdded(row={"id": "1", "city": "Paris"})]
    md = export_markdown(changes)
    assert "Added" in md
    assert "Paris" in md


def test_export_markdown_modified_row_shows_arrow():
    changes = [RowModified(key="1", before={"id": "1", "v": "a"}, after={"id": "1", "v": "b"})]
    md = export_markdown(changes)
    assert "→" in md
    assert "Modified" in md


# ---------------------------------------------------------------------------
# export_diff dispatch
# ---------------------------------------------------------------------------

def test_export_diff_dispatches_json():
    out = export_diff([], fmt="json")
    assert json.loads(out)["changes"] == []


def test_export_diff_dispatches_markdown():
    out = export_diff([], fmt="markdown")
    assert "No differences" in out


def test_export_diff_raises_on_bad_format():
    with pytest.raises(ExportError):
        export_diff([], fmt="csv")
