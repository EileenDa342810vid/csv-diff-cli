"""Unit tests for csv_diff.hedge."""
import pytest

from csv_diff.diff import RowModified, RowAdded, RowRemoved
from csv_diff.hedge import (
    HedgeError,
    HedgeRule,
    find_hedge_hits,
    format_hedge_hits,
    parse_hedge_rules,
    validate_hedge_columns,
    _crosses,
)


# ---------------------------------------------------------------------------
# parse_hedge_rules
# ---------------------------------------------------------------------------

def test_parse_hedge_rules_none_returns_none():
    assert parse_hedge_rules(None) is None


def test_parse_hedge_rules_empty_string_returns_none():
    assert parse_hedge_rules("") is None
    assert parse_hedge_rules("   ") is None


def test_parse_hedge_rules_single():
    rules = parse_hedge_rules("price:100")
    assert rules == [HedgeRule(column="price", threshold=100.0)]


def test_parse_hedge_rules_multiple():
    rules = parse_hedge_rules("price:100,qty:0")
    assert len(rules) == 2
    assert rules[0] == HedgeRule(column="price", threshold=100.0)
    assert rules[1] == HedgeRule(column="qty", threshold=0.0)


def test_parse_hedge_rules_float_threshold():
    rules = parse_hedge_rules("score:0.5")
    assert rules[0].threshold == pytest.approx(0.5)


def test_parse_hedge_rules_raises_on_missing_colon():
    with pytest.raises(HedgeError, match="expected 'column:threshold'"):
        parse_hedge_rules("price100")


def test_parse_hedge_rules_raises_on_non_numeric_threshold():
    with pytest.raises(HedgeError, match="not numeric"):
        parse_hedge_rules("price:abc")


def test_parse_hedge_rules_raises_on_empty_column():
    with pytest.raises(HedgeError, match="empty column"):
        parse_hedge_rules(":100")


# ---------------------------------------------------------------------------
# validate_hedge_columns
# ---------------------------------------------------------------------------

def test_validate_columns_all_present():
    rules = [HedgeRule(column="price", threshold=100.0)]
    validate_hedge_columns(rules, ["id", "price", "qty"])  # no exception


def test_validate_columns_raises_on_missing():
    rules = [HedgeRule(column="missing", threshold=0.0)]
    with pytest.raises(HedgeError, match="not found"):
        validate_hedge_columns(rules, ["id", "price"])


# ---------------------------------------------------------------------------
# _crosses
# ---------------------------------------------------------------------------

def test_crosses_detects_low_to_high():
    assert _crosses("50", "150", 100.0) is True


def test_crosses_detects_high_to_low():
    assert _crosses("150", "50", 100.0) is True


def test_crosses_same_side_returns_false():
    assert _crosses("10", "20", 100.0) is False


def test_crosses_non_numeric_returns_false():
    assert _crosses("n/a", "150", 100.0) is False


# ---------------------------------------------------------------------------
# find_hedge_hits
# ---------------------------------------------------------------------------

def _modified(key, old, new):
    return RowModified(key=key, old_row=old, new_row=new)


def test_find_hedge_hits_detects_crossing():
    events = [_modified("1", {"price": "80"}, {"price": "120"})]
    rules = [HedgeRule(column="price", threshold=100.0)]
    hits = find_hedge_hits(events, rules)
    assert len(hits) == 1
    assert hits[0].column == "price"
    assert hits[0].old_value == "80"
    assert hits[0].new_value == "120"


def test_find_hedge_hits_ignores_non_crossing():
    events = [_modified("1", {"price": "80"}, {"price": "90"})]
    rules = [HedgeRule(column="price", threshold=100.0)]
    assert find_hedge_hits(events, rules) == []


def test_find_hedge_hits_skips_non_modified():
    added = RowAdded(key="1", row={"price": "120"})
    removed = RowRemoved(key="2", row={"price": "80"})
    rules = [HedgeRule(column="price", threshold=100.0)]
    assert find_hedge_hits([added, removed], rules) == []


# ---------------------------------------------------------------------------
# format_hedge_hits
# ---------------------------------------------------------------------------

def test_format_hedge_hits_empty():
    output = format_hedge_hits([])
    assert "no threshold crossings" in output


def test_format_hedge_hits_contains_key_and_column():
    events = [_modified("row1", {"price": "80"}, {"price": "120"})]
    rules = [HedgeRule(column="price", threshold=100.0)]
    hits = find_hedge_hits(events, rules)
    output = format_hedge_hits(hits)
    assert "row1" in output
    assert "price" in output
    assert "80" in output
    assert "120" in output
