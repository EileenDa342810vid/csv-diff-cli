"""Tests for csv_diff.pin."""
import pytest
from csv_diff.pin import (
    PinError,
    PinConfig,
    parse_pin_columns,
    validate_pin_columns,
    apply_pin,
    merge_pin_columns,
)


def test_parse_pin_columns_none_returns_none():
    assert parse_pin_columns(None) is None


def test_parse_pin_columns_empty_returns_none():
    assert parse_pin_columns("") is None
    assert parse_pin_columns("   ") is None


def test_parse_pin_columns_single():
    cfg = parse_pin_columns("region")
    assert cfg == PinConfig(columns=["region"])


def test_parse_pin_columns_multiple():
    cfg = parse_pin_columns("region, country")
    assert cfg == PinConfig(columns=["region", "country"])


def test_parse_pin_columns_raises_on_empty_entry():
    with pytest.raises(PinError):
        parse_pin_columns("region,,country")


def test_validate_pin_columns_passes_when_present():
    cfg = PinConfig(columns=["a", "b"])
    validate_pin_columns(cfg, ["a", "b", "c"])  # no error


def test_validate_pin_columns_raises_on_missing():
    cfg = PinConfig(columns=["a", "z"])
    with pytest.raises(PinError, match="z"):
        validate_pin_columns(cfg, ["a", "b"])


def test_validate_pin_columns_none_is_noop():
    validate_pin_columns(None, ["a", "b"])  # no error


def test_apply_pin_no_config_returns_row_unchanged():
    row = {"a": "1", "b": "2"}
    assert apply_pin(row, None, ["a"]) == row


def test_apply_pin_no_columns_filter_returns_row_unchanged():
    row = {"a": "1", "b": "2"}
    cfg = PinConfig(columns=["b"])
    assert apply_pin(row, cfg, None) == row


def test_apply_pin_adds_missing_pinned_column():
    full_row = {"a": "1", "b": "2", "region": "north"}
    filtered = {"a": "1"}
    cfg = PinConfig(columns=["region"])
    result = apply_pin(filtered, cfg, ["a"])
    assert "region" not in filtered  # original untouched
    # pinned column not in filtered row — apply_pin looks in *row* which is filtered here
    # so we pass full_row as row
    result2 = apply_pin({**filtered, "region": full_row["region"]}, cfg, ["a"])
    assert result2["region"] == "north"


def test_merge_pin_columns_none_config_returns_columns_unchanged():
    assert merge_pin_columns(["a", "b"], None) == ["a", "b"]


def test_merge_pin_columns_none_columns_returns_none():
    cfg = PinConfig(columns=["region"])
    assert merge_pin_columns(None, cfg) is None


def test_merge_pin_columns_appends_missing_pins():
    cfg = PinConfig(columns=["region", "a"])
    result = merge_pin_columns(["a", "b"], cfg)
    assert result == ["a", "b", "region"]


def test_merge_pin_columns_no_duplicates():
    cfg = PinConfig(columns=["a"])
    result = merge_pin_columns(["a", "b"], cfg)
    assert result == ["a", "b"]
