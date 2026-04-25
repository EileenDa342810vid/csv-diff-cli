"""Unit tests for csv_diff.tally."""
from __future__ import annotations

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.tally import (
    TallyError,
    format_tally,
    parse_tally_columns,
    tally_diff,
    validate_tally_columns,
)


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(old_row=old, new_row=new)


# --- parse_tally_columns ---

def test_parse_tally_columns_none_returns_none():
    assert parse_tally_columns(None) is None


def test_parse_tally_columns_empty_returns_none():
    assert parse_tally_columns("") is None
    assert parse_tally_columns("   ") is None


def test_parse_tally_columns_single():
    assert parse_tally_columns("region") == ["region"]


def test_parse_tally_columns_multiple():
    assert parse_tally_columns("region,status") == ["region", "status"]


def test_parse_tally_columns_strips_whitespace():
    assert parse_tally_columns(" region , status ") == ["region", "status"]


def test_parse_tally_columns_raises_on_empty_entry():
    with pytest.raises(TallyError):
        parse_tally_columns("region,,status")


# --- validate_tally_columns ---

def test_validate_tally_columns_all_present():
    validate_tally_columns(["a", "b"], ["a", "b", "c"])  # no exception


def test_validate_tally_columns_raises_on_unknown():
    with pytest.raises(TallyError, match="unknown_col"):
        validate_tally_columns(["unknown_col"], ["a", "b"])


# --- tally_diff ---

def test_empty_diff_returns_zero_totals():
    tallies = tally_diff([], ["region"])
    assert tallies["region"].total == 0


def test_added_row_tallied():
    events = [_added({"region": "North", "status": "active"})]
    tallies = tally_diff(events, ["region"])
    assert tallies["region"].total == 1
    assert tallies["region"].unique_values["North"] == 1


def test_removed_row_tallied():
    events = [_removed({"region": "South", "status": "inactive"})]
    tallies = tally_diff(events, ["region"])
    assert tallies["region"].unique_values["South"] == 1


def test_modified_row_only_changed_columns_tallied():
    events = [
        _modified(
            {"region": "East", "status": "active"},
            {"region": "East", "status": "inactive"},
        )
    ]
    tallies = tally_diff(events, ["region", "status"])
    assert tallies["region"].total == 0  # unchanged
    assert tallies["status"].total == 1
    assert tallies["status"].unique_values["inactive"] == 1


def test_top_returns_most_frequent_value():
    events = [
        _added({"region": "North"}),
        _added({"region": "North"}),
        _added({"region": "South"}),
    ]
    tallies = tally_diff(events, ["region"])
    assert tallies["region"].top == "North"


# --- format_tally ---

def test_format_tally_empty_columns():
    output = format_tally({})
    assert "no columns" in output


def test_format_tally_contains_column_name():
    events = [_added({"region": "West"})]
    tallies = tally_diff(events, ["region"])
    output = format_tally(tallies)
    assert "region" in output
    assert "West" in output
