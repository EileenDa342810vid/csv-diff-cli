"""Tests for csv_diff.schema."""

import pytest

from csv_diff.schema import (
    ColumnSchema,
    SchemaError,
    describe_schema,
    parse_required_columns,
    validate_schema,
)


# ---------------------------------------------------------------------------
# parse_required_columns
# ---------------------------------------------------------------------------

def test_parse_required_columns_none_returns_none():
    assert parse_required_columns(None) is None


def test_parse_required_columns_empty_string_returns_none():
    assert parse_required_columns("") is None


def test_parse_required_columns_single():
    assert parse_required_columns("id") == ("id",)


def test_parse_required_columns_multiple():
    result = parse_required_columns("id,name,email")
    assert result == ("id", "name", "email")


def test_parse_required_columns_strips_whitespace():
    result = parse_required_columns(" id , name ")
    assert result == ("id", "name")


def test_parse_required_columns_raises_on_blank_entry():
    with pytest.raises(SchemaError, match="blank entry"):
        parse_required_columns("id,,name")


# ---------------------------------------------------------------------------
# validate_schema
# ---------------------------------------------------------------------------

def test_validate_schema_passes_when_all_present():
    schema = ColumnSchema(required_columns=("id", "name"))
    validate_schema(["id", "name", "email"], schema)


def test_validate_schema_raises_on_missing_column():
    schema = ColumnSchema(required_columns=("id", "missing"))
    with pytest.raises(SchemaError, match="'missing'"):
        validate_schema(["id", "name"], schema)


def test_validate_schema_reports_all_missing():
    schema = ColumnSchema(required_columns=("a", "b", "c"))
    with pytest.raises(SchemaError) as exc_info:
        validate_schema(["x"], schema)
    msg = str(exc_info.value)
    assert "'a'" in msg and "'b'" in msg and "'c'" in msg


def test_validate_schema_raises_on_missing_key_column():
    schema = ColumnSchema(required_columns=(), key_column="id")
    with pytest.raises(SchemaError, match="Key column 'id'"):
        validate_schema(["name", "email"], schema)


def test_validate_schema_passes_with_valid_key_column():
    schema = ColumnSchema(required_columns=("name",), key_column="id")
    validate_schema(["id", "name"], schema)


# ---------------------------------------------------------------------------
# describe_schema
# ---------------------------------------------------------------------------

def test_describe_schema_no_constraints():
    schema = ColumnSchema(required_columns=())
    assert describe_schema(schema) == "(no constraints)"


def test_describe_schema_required_columns_only():
    schema = ColumnSchema(required_columns=("id", "name"))
    desc = describe_schema(schema)
    assert "required columns" in desc
    assert "id" in desc and "name" in desc


def test_describe_schema_includes_key_column():
    schema = ColumnSchema(required_columns=("name",), key_column="id")
    desc = describe_schema(schema)
    assert "key column: id" in desc
