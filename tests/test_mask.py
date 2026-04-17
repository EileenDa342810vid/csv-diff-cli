"""Tests for csv_diff.mask."""

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.mask import MaskError, MaskRule, apply_mask, parse_mask_rule


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(key="k", old_row=old, new_row=new)


def test_parse_mask_rule_none_returns_none():
    assert parse_mask_rule(None) is None


def test_parse_mask_rule_empty_string_returns_none():
    assert parse_mask_rule("") is None


def test_parse_mask_rule_valid():
    rule = parse_mask_rule("status=active")
    assert rule.column == "status"
    assert rule.pattern.pattern == "active"


def test_parse_mask_rule_no_equals_raises():
    with pytest.raises(MaskError, match="column=pattern"):
        parse_mask_rule("statusactive")


def test_parse_mask_rule_empty_column_raises():
    with pytest.raises(MaskError, match="column name"):
        parse_mask_rule("=active")


def test_parse_mask_rule_empty_pattern_raises():
    with pytest.raises(MaskError, match="pattern"):
        parse_mask_rule("status=")


def test_parse_mask_rule_invalid_regex_raises():
    with pytest.raises(MaskError, match="Invalid regex"):
        parse_mask_rule("col=[invalid")


def test_apply_mask_none_rule_returns_all():
    events = [_added({"id": "1"}), _removed({"id": "2"})]
    assert apply_mask(events, None) == events


def test_apply_mask_filters_added_rows():
    rule = parse_mask_rule("status=active")
    events = [
        _added({"id": "1", "status": "active"}),
        _added({"id": "2", "status": "inactive"}),
    ]
    result = apply_mask(events, rule)
    assert len(result) == 1
    assert result[0].row["id"] == "1"


def test_apply_mask_filters_removed_rows():
    rule = parse_mask_rule("region=EU")
    events = [
        _removed({"id": "1", "region": "EU"}),
        _removed({"id": "2", "region": "US"}),
    ]
    result = apply_mask(events, rule)
    assert len(result) == 1


def test_apply_mask_uses_new_row_for_modified():
    rule = parse_mask_rule("status=open")
    events = [
        _modified({"id": "1", "status": "closed"}, {"id": "1", "status": "open"}),
        _modified({"id": "2", "status": "open"}, {"id": "2", "status": "closed"}),
    ]
    result = apply_mask(events, rule)
    assert len(result) == 1


def test_apply_mask_regex_partial_match():
    rule = parse_mask_rule("name=^Alice")
    events = [
        _added({"name": "Alice Smith"}),
        _added({"name": "Bob Alice"}),
    ]
    result = apply_mask(events, rule)
    assert len(result) == 1
    assert result[0].row["name"] == "Alice Smith"
