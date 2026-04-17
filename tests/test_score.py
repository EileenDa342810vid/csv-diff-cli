"""Unit tests for csv_diff.score."""
import pytest
from csv_diff.score import (
    ScoreError,
    SimilarityScore,
    compute_score,
    format_score,
    _grade,
)
from csv_diff.diff import RowAdded, RowRemoved, RowModified


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(old_row=old, new_row=new)


def test_empty_diff_perfect_score():
    s = compute_score([], 10)
    assert s.score == 1.0
    assert s.grade == "A"
    assert s.changed_rows == 0


def test_all_changed_zero_score():
    diff = [_added({"id": "1"})] * 10
    s = compute_score(diff, 10)
    assert s.score == 0.0
    assert s.grade == "F"


def test_partial_changes():
    diff = [_added({"id": "1"}), _removed({"id": "2"})]
    s = compute_score(diff, 10)
    assert s.changed_rows == 2
    assert s.score == pytest.approx(0.8)


def test_zero_total_rows_gives_perfect_score():
    s = compute_score([], 0)
    assert s.score == 1.0


def test_negative_total_rows_raises():
    with pytest.raises(ScoreError):
        compute_score([], -1)


def test_grade_boundaries():
    assert _grade(1.0) == "A"
    assert _grade(0.95) == "A"
    assert _grade(0.80) == "B"
    assert _grade(0.60) == "C"
    assert _grade(0.40) == "D"
    assert _grade(0.39) == "F"


def test_format_score_contains_fields():
    s = SimilarityScore(total_rows=20, changed_rows=4, score=0.8, grade="B")
    out = format_score(s)
    assert "80.00%" in out
    assert "Grade" in out
    assert "B" in out
    assert "20" in out
