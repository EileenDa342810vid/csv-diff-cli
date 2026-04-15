"""Additional formatting tests for csv_diff.stats.format_stats."""
from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.stats import compute_stats, format_stats


def _modified(key: str, cols: list[str]) -> RowModified:
    changes = {c: ("old", "new") for c in cols}
    return RowModified(key=key, old_row={}, new_row={}, changes=changes)


def test_summary_header_always_present():
    stats = compute_stats([])
    assert "=== Diff Summary ===" in format_stats(stats)


def test_unchanged_shown_when_nonzero():
    stats = compute_stats(
        [RowAdded(key="1", row={})], total_rows=10
    )
    output = format_stats(stats)
    assert "Unchanged" in output
    assert "9" in output


def test_unchanged_hidden_when_zero():
    stats = compute_stats(
        [RowAdded(key="1", row={})], total_rows=1
    )
    output = format_stats(stats)
    assert "Unchanged" not in output


def test_no_modified_columns_section_when_none():
    stats = compute_stats(
        [RowAdded(key="1", row={})]
    )
    output = format_stats(stats)
    assert "Most-changed" not in output


def test_multiple_columns_all_appear():
    diff = [_modified("1", ["alpha", "beta", "gamma"])]
    stats = compute_stats(diff)
    output = format_stats(stats)
    for col in ("alpha", "beta", "gamma"):
        assert col in output
