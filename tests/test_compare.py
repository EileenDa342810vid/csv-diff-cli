"""Tests for csv_diff.compare."""

import pytest

from csv_diff.compare import (
    CompareError,
    ToleranceConfig,
    build_tolerance_map,
    parse_tolerance_specs,
    validate_tolerance_columns,
    values_equal,
)


def test_parse_tolerance_specs_none_returns_none():
    assert parse_tolerance_specs(None) is None


def test_parse_tolerance_specs_empty_returns_none():
    assert parse_tolerance_specs("") is None


def test_parse_tolerance_specs_single():
    result = parse_tolerance_specs("price:0.01")
    assert result == [ToleranceConfig(column="price", tolerance=0.01)]


def test_parse_tolerance_specs_multiple():
    result = parse_tolerance_specs("price:0.01, qty:5")
    assert len(result) == 2
    assert result[0].column == "price"
    assert result[1].column == "qty"
    assert result[1].tolerance == 5.0


def test_parse_tolerance_specs_raises_on_missing_colon():
    with pytest.raises(CompareError, match="Invalid tolerance spec"):
        parse_tolerance_specs("price0.01")


def test_parse_tolerance_specs_raises_on_empty_column():
    with pytest.raises(CompareError, match="Empty column name"):
        parse_tolerance_specs(":0.01")


def test_parse_tolerance_specs_raises_on_non_numeric_value():
    with pytest.raises(CompareError, match="Non-numeric tolerance"):
        parse_tolerance_specs("price:abc")


def test_parse_tolerance_specs_raises_on_negative():
    with pytest.raises(CompareError, match=">= 0"):
        parse_tolerance_specs("price:-1")


def test_validate_tolerance_columns_ok():
    configs = [ToleranceConfig(column="price", tolerance=0.01)]
    validate_tolerance_columns(configs, ["id", "price", "qty"])


def test_validate_tolerance_columns_raises_on_unknown():
    configs = [ToleranceConfig(column="missing", tolerance=0.01)]
    with pytest.raises(CompareError, match="not found in headers"):
        validate_tolerance_columns(configs, ["id", "price"])


def test_values_equal_identical_strings():
    assert values_equal("name", "foo", "foo") is True


def test_values_equal_different_strings_no_tolerance():
    assert values_equal("name", "foo", "bar") is False


def test_values_equal_within_tolerance():
    tmap = {"price": 0.05}
    assert values_equal("price", "1.00", "1.04", tmap) is True


def test_values_equal_outside_tolerance():
    tmap = {"price": 0.05}
    assert values_equal("price", "1.00", "1.10", tmap) is False


def test_values_equal_non_numeric_with_tolerance():
    tmap = {"price": 0.05}
    assert values_equal("price", "n/a", "1.00", tmap) is False


def test_build_tolerance_map_none_returns_empty():
    assert build_tolerance_map(None) == {}


def test_build_tolerance_map_returns_dict():
    configs = [ToleranceConfig("price", 0.01), ToleranceConfig("qty", 2.0)]
    assert build_tolerance_map(configs) == {"price": 0.01, "qty": 2.0}
