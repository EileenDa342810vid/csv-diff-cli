"""Tests for csv_diff.heatmap."""
from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.heatmap import (
    HeatmapResult,
    compute_heatmap,
    format_heatmap,
)

COLS = ["id", "name", "score"]


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(key=old.get("id", "?"), old_row=old, new_row=new)


# ---------------------------------------------------------------------------
# compute_heatmap
# ---------------------------------------------------------------------------

def test_empty_diff_returns_zero_counts():
    result = compute_heatmap([], COLS)
    assert result.total() == 0
    assert result.hottest() is None


def test_added_row_increments_all_columns():
    events = [_added({"id": "1", "name": "Alice", "score": "10"})]
    result = compute_heatmap(events, COLS)
    assert result.counts["id"] == 1
    assert result.counts["name"] == 1
    assert result.counts["score"] == 1


def test_removed_row_increments_all_columns():
    events = [_removed({"id": "2", "name": "Bob", "score": "20"})]
    result = compute_heatmap(events, COLS)
    assert result.total() == 3


def test_modified_row_only_increments_changed_columns():
    old = {"id": "3", "name": "Carol", "score": "30"}
    new = {"id": "3", "name": "Carol", "score": "99"}
    events = [_modified(old, new)]
    result = compute_heatmap(events, COLS)
    assert result.counts.get("id", 0) == 0
    assert result.counts.get("name", 0) == 0
    assert result.counts["score"] == 1


def test_multiple_events_accumulate_counts():
    events = [
        _modified(
            {"id": "1", "name": "A", "score": "1"},
            {"id": "1", "name": "B", "score": "1"},
        ),
        _modified(
            {"id": "2", "name": "C", "score": "5"},
            {"id": "2", "name": "D", "score": "9"},
        ),
    ]
    result = compute_heatmap(events, COLS)
    assert result.counts["name"] == 2
    assert result.counts["score"] == 1


def test_hottest_returns_most_changed_column():
    events = [
        _added({"id": "1", "name": "X", "score": "0"}),
        _modified(
            {"id": "2", "name": "Y", "score": "1"},
            {"id": "2", "name": "Z", "score": "1"},
        ),
    ]
    result = compute_heatmap(events, COLS)
    # id and score each appear once (from added); name appears twice
    assert result.hottest() == "name"


def test_columns_not_in_row_are_skipped():
    events = [_added({"id": "1"})]
    result = compute_heatmap(events, COLS)
    assert result.counts.get("name", 0) == 0
    assert result.counts.get("score", 0) == 0


# ---------------------------------------------------------------------------
# format_heatmap
# ---------------------------------------------------------------------------

def test_format_heatmap_contains_column_header():
    result = compute_heatmap([], COLS)
    output = format_heatmap(result)
    assert "Column Change Frequency" in output


def test_format_heatmap_lists_all_columns():
    result = compute_heatmap([], COLS)
    output = format_heatmap(result)
    for col in COLS:
        assert col in output


def test_format_heatmap_shows_total():
    events = [_added({"id": "1", "name": "A", "score": "5"})]
    result = compute_heatmap(events, COLS)
    output = format_heatmap(result)
    assert "TOTAL" in output
    assert "3" in output


def test_format_heatmap_empty_columns():
    result = HeatmapResult(columns=[])
    assert format_heatmap(result) == "(no columns)"
