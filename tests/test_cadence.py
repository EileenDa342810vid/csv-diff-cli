"""Tests for csv_diff.cadence."""
from __future__ import annotations

import pytest

from csv_diff.cadence import (
    CadenceError,
    CadenceResult,
    _grade,
    compute_cadence,
    format_cadence,
    parse_cadence_column,
)
from csv_diff.diff import RowAdded, RowModified, RowRemoved


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(row: dict) -> RowAdded:
    return RowAdded(row=row)


def _removed(row: dict) -> RowRemoved:
    return RowRemoved(row=row)


def _modified(old: dict, new: dict) -> RowModified:
    diffs = {k: (old[k], new[k]) for k in old if old.get(k) != new.get(k)}
    return RowModified(old_row=old, new_row=new, differences=diffs)


# ---------------------------------------------------------------------------
# parse_cadence_column
# ---------------------------------------------------------------------------

def test_parse_cadence_column_none_returns_none():
    assert parse_cadence_column(None) is None


def test_parse_cadence_column_empty_returns_none():
    assert parse_cadence_column("  ") is None


def test_parse_cadence_column_strips_whitespace():
    assert parse_cadence_column("  score  ") == "score"


# ---------------------------------------------------------------------------
# _grade
# ---------------------------------------------------------------------------

def test_grade_zero_is_none():
    assert _grade(0.0) == "NONE"


def test_grade_low():
    assert _grade(0.1) == "LOW"


def test_grade_medium():
    assert _grade(0.5) == "MEDIUM"


def test_grade_high():
    assert _grade(0.9) == "HIGH"


# ---------------------------------------------------------------------------
# compute_cadence
# ---------------------------------------------------------------------------

def test_empty_diff_zero_rate():
    result = compute_cadence([], total_rows=10)
    assert result.changed_rows == 0
    assert result.change_rate == 0.0
    assert result.grade == "NONE"


def test_all_added_full_rate():
    diff = [_added({"id": str(i)}) for i in range(4)]
    result = compute_cadence(diff, total_rows=4)
    assert result.changed_rows == 4
    assert result.change_rate == 1.0
    assert result.grade == "HIGH"


def test_partial_modified_medium_grade():
    diff = [_modified({"id": "1", "v": "a"}, {"id": "1", "v": "b"}),
            _modified({"id": "2", "v": "c"}, {"id": "2", "v": "d"})]
    result = compute_cadence(diff, total_rows=4)
    assert result.changed_rows == 2
    assert result.change_rate == 0.5


def test_removed_row_counted():
    diff = [_removed({"id": "99", "val": "x"})]
    result = compute_cadence(diff, total_rows=5)
    assert result.changed_rows == 1


def test_focus_column_populated():
    diff = [
        _modified({"id": "1", "score": "10"}, {"id": "1", "score": "20"}),
        _modified({"id": "2", "name": "a"}, {"id": "2", "name": "b"}),
    ]
    result = compute_cadence(diff, total_rows=4, focus_column="score")
    assert "score" in result.column_rates
    # only 1 of 4 rows changed the 'score' column
    assert result.column_rates["score"] == 0.25


def test_negative_total_rows_raises():
    with pytest.raises(CadenceError):
        compute_cadence([], total_rows=-1)


def test_zero_total_rows_returns_zero_rate():
    result = compute_cadence([], total_rows=0)
    assert result.change_rate == 0.0


# ---------------------------------------------------------------------------
# format_cadence
# ---------------------------------------------------------------------------

def test_format_cadence_contains_header():
    result = CadenceResult(total_rows=10, changed_rows=3,
                           change_rate=0.3, grade="MEDIUM")
    text = format_cadence(result)
    assert "=== Change Cadence ===" in text
    assert "30.0%" in text
    assert "MEDIUM" in text


def test_format_cadence_shows_column_rate():
    result = CadenceResult(total_rows=10, changed_rows=2,
                           change_rate=0.2, grade="LOW",
                           column_rates={"price": 0.1})
    text = format_cadence(result)
    assert "price" in text
    assert "10.0%" in text
