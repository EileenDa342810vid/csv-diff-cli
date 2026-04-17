"""Tests for csv_diff.cast."""

import pytest

from csv_diff.cast import (
    CastError,
    ColumnCast,
    apply_casts,
    cast_rows,
    parse_casts,
    validate_casts,
)


def test_parse_casts_none_returns_none():
    assert parse_casts(None) is None


def test_parse_casts_empty_string_returns_none():
    assert parse_casts("") is None


def test_parse_casts_single():
    result = parse_casts("age:int")
    assert result == [ColumnCast(column="age", type_name="int")]


def test_parse_casts_multiple():
    result = parse_casts("age:int, score:float")
    assert result == [
        ColumnCast(column="age", type_name="int"),
        ColumnCast(column="score", type_name="float"),
    ]


def test_parse_casts_normalises_type_case():
    result = parse_casts("active:BOOL")
    assert result[0].type_name == "bool"


def test_parse_casts_raises_on_missing_colon():
    with pytest.raises(CastError, match="expected 'column:type'"):
        parse_casts("ageint")


def test_parse_casts_raises_on_unknown_type():
    with pytest.raises(CastError, match="Unsupported type"):
        parse_casts("age:integer")


def test_parse_casts_raises_on_empty_column():
    with pytest.raises(CastError, match="Empty column name"):
        parse_casts(":int")


def test_validate_casts_passes_when_all_present():
    casts = [ColumnCast(column="age", type_name="int")]
    validate_casts(casts, ["name", "age"])


def test_validate_casts_raises_on_missing_column():
    casts = [ColumnCast(column="missing", type_name="int")]
    with pytest.raises(CastError, match="not found in headers"):
        validate_casts(casts, ["name", "age"])


def test_apply_casts_int():
    row = {"name": "Alice", "age": "30.0"}
    result = apply_casts(row, [ColumnCast(column="age", type_name="int")])
    assert result["age"] == "30"
    assert result["name"] == "Alice"


def test_apply_casts_float():
    row = {"score": "9"}
    result = apply_casts(row, [ColumnCast(column="score", type_name="float")])
    assert result["score"] == "9.0"


def test_apply_casts_bool_true_values():
    for val in ("1", "true", "yes", "True", "YES"):
        row = {"active": val}
        result = apply_casts(row, [ColumnCast(column="active", type_name="bool")])
        assert result["active"] == "True"


def test_apply_casts_bool_false_values():
    row = {"active": "0"}
    result = apply_casts(row, [ColumnCast(column="active", type_name="bool")])
    assert result["active"] == "False"


def test_apply_casts_raises_on_bad_value():
    row = {"age": "not-a-number"}
    with pytest.raises(CastError, match="Cannot cast"):
        apply_casts(row, [ColumnCast(column="age", type_name="int")])


def test_cast_rows_none_returns_unchanged():
    rows = [{"a": "1"}, {"a": "2"}]
    assert cast_rows(rows, None) is rows


def test_cast_rows_applies_to_all_rows():
    rows = [{"age": "1"}, {"age": "2"}]
    result = cast_rows(rows, [ColumnCast(column="age", type_name="float")])
    assert [r["age"] for r in result] == ["1.0", "2.0"]
