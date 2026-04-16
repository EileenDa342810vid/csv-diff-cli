"""Tests for csv_diff.transform."""

import pytest
from csv_diff.transform import (
    TransformError,
    apply_transforms,
    parse_transforms,
    transform_rows,
    validate_transforms,
)


def test_parse_transforms_none_returns_none():
    assert parse_transforms(None) is None


def test_parse_transforms_empty_string_returns_none():
    assert parse_transforms("") is None


def test_parse_transforms_single():
    result = parse_transforms("name:upper")
    assert result == {"name": "upper"}


def test_parse_transforms_multiple():
    result = parse_transforms("name:upper,city:lower")
    assert result == {"name": "upper", "city": "lower"}


def test_parse_transforms_strips_whitespace():
    result = parse_transforms(" name : strip ")
    assert result == {"name": "strip"}


def test_parse_transforms_raises_on_missing_colon():
    with pytest.raises(TransformError, match="Invalid transform spec"):
        parse_transforms("nameupper")


def test_parse_transforms_raises_on_unknown_transform():
    with pytest.raises(TransformError, match="Unknown transform"):
        parse_transforms("name:reverse")


def test_parse_transforms_raises_on_empty_column():
    with pytest.raises(TransformError, match="Column name must not be empty"):
        parse_transforms(":upper")


def test_validate_transforms_passes_when_columns_present():
    validate_transforms({"name": "upper"}, ["id", "name", "city"])


def test_validate_transforms_raises_on_missing_column():
    with pytest.raises(TransformError, match="not in CSV headers"):
        validate_transforms({"missing": "lower"}, ["id", "name"])


def test_apply_transforms_upper():
    row = {"id": "1", "name": "alice"}
    result = apply_transforms(row, {"name": "upper"})
    assert result["name"] == "ALICE"
    assert result["id"] == "1"


def test_apply_transforms_does_not_mutate_original():
    row = {"name": "alice"}
    apply_transforms(row, {"name": "upper"})
    assert row["name"] == "alice"


def test_transform_rows_none_returns_original():
    rows = [{"name": "alice"}]
    assert transform_rows(rows, None) is rows


def test_transform_rows_applies_to_all():
    rows = [{"name": "alice"}, {"name": "bob"}]
    result = transform_rows(rows, {"name": "title"})
    assert [r["name"] for r in result] == ["Alice", "Bob"]
