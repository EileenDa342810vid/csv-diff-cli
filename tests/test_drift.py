"""Tests for csv_diff.drift."""

import pytest

from csv_diff.drift import SchemaDrift, detect_drift, format_drift


def test_no_drift_identical_headers():
    drift = detect_drift(["id", "name", "value"], ["id", "name", "value"])
    assert not drift.has_drift
    assert drift.added_columns == []
    assert drift.removed_columns == []
    assert drift.reordered is False


def test_detects_added_column():
    drift = detect_drift(["id", "name"], ["id", "name", "email"])
    assert drift.added_columns == ["email"]
    assert drift.removed_columns == []
    assert drift.has_drift


def test_detects_removed_column():
    drift = detect_drift(["id", "name", "email"], ["id", "name"])
    assert drift.removed_columns == ["email"]
    assert drift.added_columns == []
    assert drift.has_drift


def test_detects_reordered_columns():
    drift = detect_drift(["id", "name", "value"], ["id", "value", "name"])
    assert drift.reordered is True
    assert drift.added_columns == []
    assert drift.removed_columns == []
    assert drift.has_drift


def test_detects_added_and_removed_simultaneously():
    drift = detect_drift(["id", "old_col"], ["id", "new_col"])
    assert "old_col" in drift.removed_columns
    assert "new_col" in drift.added_columns


def test_format_drift_returns_none_when_no_drift():
    drift = SchemaDrift()
    assert format_drift(drift) is None


def test_format_drift_mentions_added_columns():
    drift = detect_drift(["id"], ["id", "score"])
    report = format_drift(drift)
    assert report is not None
    assert "score" in report
    assert "Added" in report


def test_format_drift_mentions_removed_columns():
    drift = detect_drift(["id", "legacy"], ["id"])
    report = format_drift(drift)
    assert "legacy" in report
    assert "Removed" in report


def test_format_drift_mentions_reorder():
    drift = detect_drift(["a", "b", "c"], ["a", "c", "b"])
    report = format_drift(drift)
    assert "order" in report.lower()
