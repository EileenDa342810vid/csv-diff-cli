"""Tests for csv_diff.coalesce."""

import pytest

from csv_diff.coalesce import (
    CoalesceConfig,
    CoalesceError,
    coalesce_rows,
    parse_coalesce_columns,
    validate_coalesce_columns,
)


# ---------------------------------------------------------------------------
# parse_coalesce_columns
# ---------------------------------------------------------------------------

def test_parse_coalesce_columns_none_returns_none():
    assert parse_coalesce_columns(None) is None


def test_parse_coalesce_columns_empty_string_returns_none():
    assert parse_coalesce_columns("") is None
    assert parse_coalesce_columns("   ") is None


def test_parse_coalesce_columns_single():
    result = parse_coalesce_columns("region")
    assert result == CoalesceConfig(columns=["region"])


def test_parse_coalesce_columns_multiple():
    result = parse_coalesce_columns("region, category")
    assert result == CoalesceConfig(columns=["region", "category"])


def test_parse_coalesce_columns_raises_on_empty_entry():
    with pytest.raises(CoalesceError, match="empty entry"):
        parse_coalesce_columns("region,,category")


# ---------------------------------------------------------------------------
# validate_coalesce_columns
# ---------------------------------------------------------------------------

def test_validate_coalesce_columns_passes_when_all_present():
    cfg = CoalesceConfig(columns=["a", "b"])
    validate_coalesce_columns(cfg, ["a", "b", "c"])  # should not raise


def test_validate_coalesce_columns_raises_on_missing():
    cfg = CoalesceConfig(columns=["a", "z"])
    with pytest.raises(CoalesceError, match="z"):
        validate_coalesce_columns(cfg, ["a", "b"])


# ---------------------------------------------------------------------------
# coalesce_rows
# ---------------------------------------------------------------------------

_ROWS = [
    {"region": "North", "value": "10"},
    {"region": "",      "value": "20"},
    {"region": "",      "value": "30"},
    {"region": "South", "value": "40"},
    {"region": "",      "value": "50"},
]


def test_coalesce_fills_empty_values():
    cfg = CoalesceConfig(columns=["region"])
    result = coalesce_rows(_ROWS, cfg)
    regions = [r["region"] for r in result]
    assert regions == ["North", "North", "North", "South", "South"]


def test_coalesce_leaves_non_target_columns_unchanged():
    cfg = CoalesceConfig(columns=["region"])
    result = coalesce_rows(_ROWS, cfg)
    values = [r["value"] for r in result]
    assert values == ["10", "20", "30", "40", "50"]


def test_coalesce_empty_rows_returns_empty():
    cfg = CoalesceConfig(columns=["region"])
    assert coalesce_rows([], cfg) == []


def test_coalesce_leading_empty_stays_empty():
    rows = [
        {"region": "", "value": "1"},
        {"region": "East", "value": "2"},
    ]
    cfg = CoalesceConfig(columns=["region"])
    result = coalesce_rows(rows, cfg)
    assert result[0]["region"] == ""
    assert result[1]["region"] == "East"


def test_coalesce_does_not_mutate_original_rows():
    rows = [{"region": "", "value": "1"}]
    cfg = CoalesceConfig(columns=["region"])
    coalesce_rows(rows, cfg)
    assert rows[0]["region"] == ""
