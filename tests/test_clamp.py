"""Tests for csv_diff.clamp."""

import pytest

from csv_diff.clamp import (
    ClampError,
    ClampRule,
    apply_clamps,
    clamp_rows,
    parse_clamp_rules,
    validate_clamp_rules,
)


def test_parse_clamp_rules_none_returns_none():
    assert parse_clamp_rules(None) is None


def test_parse_clamp_rules_empty_string_returns_none():
    assert parse_clamp_rules("") is None


def test_parse_clamp_rules_single():
    rules = parse_clamp_rules("age:0:120")
    assert rules == [ClampRule(column="age", min_val=0.0, max_val=120.0)]


def test_parse_clamp_rules_multiple():
    rules = parse_clamp_rules("age:0:120,score::100")
    assert len(rules) == 2
    assert rules[0].column == "age"
    assert rules[1].column == "score"
    assert rules[1].min_val is None
    assert rules[1].max_val == 100.0


def test_parse_clamp_rules_open_lower_bound():
    rules = parse_clamp_rules("val::50")
    assert rules[0].min_val is None
    assert rules[0].max_val == 50.0


def test_parse_clamp_rules_raises_on_empty_entry():
    with pytest.raises(ClampError, match="Empty clamp entry"):
        parse_clamp_rules("age:0:120,,score:0:10")


def test_parse_clamp_rules_raises_on_bad_format():
    with pytest.raises(ClampError, match="must be 'column:min:max'"):
        parse_clamp_rules("age:0")


def test_parse_clamp_rules_raises_on_non_numeric():
    with pytest.raises(ClampError, match="Non-numeric bound"):
        parse_clamp_rules("age:low:high")


def test_parse_clamp_rules_raises_when_min_exceeds_max():
    with pytest.raises(ClampError, match="min .* exceeds max"):
        parse_clamp_rules("age:100:0")


def test_validate_clamp_rules_passes_when_all_present():
    rules = [ClampRule("age", 0, 120)]
    validate_clamp_rules(rules, ["name", "age"])


def test_validate_clamp_rules_raises_on_missing_column():
    rules = [ClampRule("score", 0, 100)]
    with pytest.raises(ClampError, match="not found in headers"):
        validate_clamp_rules(rules, ["name", "age"])


def test_apply_clamps_clamps_above_max():
    row = {"age": "200", "name": "Alice"}
    result = apply_clamps(row, [ClampRule("age", 0.0, 120.0)])
    assert result["age"] == "120"


def test_apply_clamps_clamps_below_min():
    row = {"score": "-5"}
    result = apply_clamps(row, [ClampRule("score", 0.0, 100.0)])
    assert result["score"] == "0"


def test_apply_clamps_leaves_in_range_unchanged():
    row = {"age": "30"}
    result = apply_clamps(row, [ClampRule("age", 0.0, 120.0)])
    assert result["age"] == "30"


def test_apply_clamps_ignores_non_numeric():
    row = {"age": "unknown"}
    result = apply_clamps(row, [ClampRule("age", 0.0, 120.0)])
    assert result["age"] == "unknown"


def test_clamp_rows_none_rules_returns_original():
    rows = [{"age": "200"}]
    assert clamp_rows(rows, None) is rows


def test_clamp_rows_applies_to_all_rows():
    rows = [{"age": "5"}, {"age": "200"}]
    result = clamp_rows(rows, [ClampRule("age", 10.0, 150.0)])
    assert result[0]["age"] == "10"
    assert result[1]["age"] == "150"
