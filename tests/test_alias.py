"""Tests for csv_diff.alias."""

import pytest

from csv_diff.alias import (
    AliasError,
    ColumnAlias,
    apply_aliases,
    parse_aliases,
    rename_headers,
    validate_aliases,
)


def test_parse_aliases_none_returns_none():
    assert parse_aliases(None) is None


def test_parse_aliases_empty_string_returns_none():
    assert parse_aliases("") is None


def test_parse_aliases_single():
    result = parse_aliases("name:full_name")
    assert result == ColumnAlias(mapping={"name": "full_name"})


def test_parse_aliases_multiple():
    result = parse_aliases("a:alpha,b:beta")
    assert result == ColumnAlias(mapping={"a": "alpha", "b": "beta"})


def test_parse_aliases_strips_whitespace():
    result = parse_aliases(" a : alpha , b : beta ")
    assert result.mapping == {"a": "alpha", "b": "beta"}


def test_parse_aliases_raises_on_missing_colon():
    with pytest.raises(AliasError, match="expected 'original:alias' format"):
        parse_aliases("badentry")


def test_parse_aliases_raises_on_empty_original():
    with pytest.raises(AliasError, match="non-empty"):
        parse_aliases(":alias")


def test_parse_aliases_raises_on_empty_alias():
    with pytest.raises(AliasError, match="non-empty"):
        parse_aliases("original:")


def test_validate_aliases_passes_when_all_present():
    alias = ColumnAlias(mapping={"a": "alpha"})
    validate_aliases(alias, ["a", "b", "c"])  # should not raise


def test_validate_aliases_raises_on_missing_column():
    alias = ColumnAlias(mapping={"x": "ex"})
    with pytest.raises(AliasError, match="x"):
        validate_aliases(alias, ["a", "b"])


def test_apply_aliases_renames_keys():
    alias = ColumnAlias(mapping={"name": "full_name"})
    row = {"name": "Alice", "age": "30"}
    assert apply_aliases(row, alias) == {"full_name": "Alice", "age": "30"}


def test_apply_aliases_none_returns_original():
    row = {"name": "Alice"}
    assert apply_aliases(row, None) is row


def test_rename_headers_applies_mapping():
    alias = ColumnAlias(mapping={"a": "alpha", "c": "gamma"})
    assert rename_headers(["a", "b", "c"], alias) == ["alpha", "b", "gamma"]


def test_rename_headers_none_returns_original():
    headers = ["a", "b"]
    assert rename_headers(headers, None) == headers
