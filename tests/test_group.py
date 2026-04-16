import pytest
from csv_diff.group import (
    GroupError, ColumnGroup, parse_group_by, validate_group_column,
    group_diff, format_groups,
)
from csv_diff.diff import RowAdded, RowRemoved, RowModified


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(before, after):
    return RowModified(before=before, after=after)


def test_parse_group_by_none_returns_none():
    assert parse_group_by(None) is None


def test_parse_group_by_empty_returns_none():
    assert parse_group_by("") is None
    assert parse_group_by("   ") is None


def test_parse_group_by_strips_whitespace():
    assert parse_group_by("  region  ") == "region"


def test_validate_group_column_ok():
    validate_group_column("region", ["id", "region", "value"])


def test_validate_group_column_raises():
    with pytest.raises(GroupError, match="region"):
        validate_group_column("region", ["id", "value"])


def test_group_diff_empty():
    assert group_diff([], "region") == {}


def test_group_diff_added_rows():
    events = [
        _added({"id": "1", "region": "EU", "val": "10"}),
        _added({"id": "2", "region": "US", "val": "20"}),
        _added({"id": "3", "region": "EU", "val": "30"}),
    ]
    groups = group_diff(events, "region")
    assert len(groups["EU"].added) == 2
    assert len(groups["US"].added) == 1


def test_group_diff_removed_rows():
    events = [_removed({"id": "1", "region": "APAC", "val": "5"})]
    groups = group_diff(events, "region")
    assert len(groups["APAC"].removed) == 1


def test_group_diff_modified_uses_before():
    events = [_modified(
        {"id": "1", "region": "EU", "val": "old"},
        {"id": "1", "region": "US", "val": "new"},
    )]
    groups = group_diff(events, "region")
    assert "EU" in groups
    assert len(groups["EU"].modified) == 1


def test_group_diff_total():
    events = [
        _added({"id": "1", "region": "EU", "val": "1"}),
        _removed({"id": "2", "region": "EU", "val": "2"}),
        _modified({"id": "3", "region": "EU", "val": "a"}, {"id": "3", "region": "EU", "val": "b"}),
    ]
    groups = group_diff(events, "region")
    assert groups["EU"].total == 3


def test_format_groups_no_changes():
    result = format_groups({}, "region")
    assert "No changes" in result


def test_format_groups_shows_column_name():
    events = [_added({"id": "1", "region": "EU", "val": "1"})]
    groups = group_diff(events, "region")
    result = format_groups(groups, "region")
    assert "region" in result
    assert "EU" in result
