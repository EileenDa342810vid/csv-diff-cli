"""Unit tests for csv_diff.tag."""

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.tag import (
    TagError,
    TagRule,
    TaggedEvent,
    format_tags,
    parse_tag_rules,
    tag_diff,
    tag_event,
)


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(key="k", old_row=old, new_row=new)


def test_parse_tag_rules_none_returns_none():
    assert parse_tag_rules(None) is None


def test_parse_tag_rules_empty_string_returns_none():
    assert parse_tag_rules("") is None


def test_parse_tag_rules_single():
    rules = parse_tag_rules("urgent:status:FAIL")
    assert len(rules) == 1
    assert rules[0].label == "urgent"
    assert rules[0].column == "status"


def test_parse_tag_rules_multiple():
    rules = parse_tag_rules("hi:col:X, lo:col:Y")
    assert [r.label for r in rules] == ["hi", "lo"]


def test_parse_tag_rules_raises_on_bad_format():
    with pytest.raises(TagError, match="expected"):
        parse_tag_rules("badspec")


def test_parse_tag_rules_raises_on_bad_regex():
    with pytest.raises(TagError, match="Bad regex"):
        parse_tag_rules("x:col:[invalid")


def test_tag_event_matches_added_row():
    rules = parse_tag_rules("flag:status:FAIL")
    event = _added({"id": "1", "status": "FAIL"})
    te = tag_event(event, rules)
    assert "flag" in te.tags


def test_tag_event_no_match():
    rules = parse_tag_rules("flag:status:FAIL")
    event = _added({"id": "1", "status": "OK"})
    te = tag_event(event, rules)
    assert te.tags == []


def test_tag_event_uses_new_row_for_modified():
    rules = parse_tag_rules("flag:status:FAIL")
    event = _modified({"id": "1", "status": "OK"}, {"id": "1", "status": "FAIL"})
    te = tag_event(event, rules)
    assert "flag" in te.tags


def test_tag_diff_no_rules_wraps_events():
    events = [_added({"id": "1"})]
    result = tag_diff(events, None)
    assert len(result) == 1
    assert result[0].tags == []


def test_format_tags_empty():
    te = TaggedEvent(event=None, tags=[])
    assert format_tags(te) == ""


def test_format_tags_with_labels():
    te = TaggedEvent(event=None, tags=["urgent", "review"])
    assert format_tags(te) == "[urgent, review]"
