"""Tests for csv_diff.context."""
import pytest

from csv_diff.context import (
    ContextError,
    ContextRow,
    add_context,
    parse_context_lines,
)
from csv_diff.diff import RowAdded, RowModified, RowRemoved


# ---------------------------------------------------------------------------
# parse_context_lines
# ---------------------------------------------------------------------------

def test_parse_context_lines_none_returns_none():
    assert parse_context_lines(None) is None


def test_parse_context_lines_integer_passthrough():
    assert parse_context_lines(3) == 3


def test_parse_context_lines_string_integer():
    assert parse_context_lines("2") == 2


def test_parse_context_lines_zero_allowed():
    assert parse_context_lines(0) == 0


def test_parse_context_lines_raises_on_negative():
    with pytest.raises(ContextError, match=">= 0"):
        parse_context_lines(-1)


def test_parse_context_lines_raises_on_non_integer():
    with pytest.raises(ContextError, match="non-negative integer"):
        parse_context_lines("abc")


# ---------------------------------------------------------------------------
# add_context helpers
# ---------------------------------------------------------------------------

ROWS = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
    {"id": "4", "name": "Dave"},
    {"id": "5", "name": "Eve"},
]


def test_zero_context_returns_only_diff_events():
    diff = [RowRemoved(row=ROWS[2])]
    result = add_context(diff, ROWS, key_col="id", n=0)
    assert result == diff


def test_context_includes_neighbouring_unchanged_rows():
    diff = [RowRemoved(row=ROWS[2])]  # Carol removed
    result = add_context(diff, ROWS, key_col="id", n=1)
    context_rows = [r for r in result if isinstance(r, ContextRow)]
    context_names = {r.row["name"] for r in context_rows}
    # Bob and Dave are immediate neighbours of Carol
    assert "Bob" in context_names
    assert "Dave" in context_names


def test_context_does_not_include_changed_row_as_context():
    diff = [RowRemoved(row=ROWS[2])]
    result = add_context(diff, ROWS, key_col="id", n=2)
    context_rows = [r for r in result if isinstance(r, ContextRow)]
    context_names = {r.row["name"] for r in context_rows}
    assert "Carol" not in context_names


def test_added_rows_do_not_generate_context_from_old_file():
    new_row = {"id": "6", "name": "Frank"}
    diff = [RowAdded(row=new_row)]
    result = add_context(diff, ROWS, key_col="id", n=2)
    context_rows = [r for r in result if isinstance(r, ContextRow)]
    # No old-file neighbour exists for a purely added row
    assert context_rows == []


def test_modified_row_generates_context():
    old = ROWS[1]  # Bob
    new = {"id": "2", "name": "Bobby"}
    diff = [RowModified(old_row=old, new_row=new)]
    result = add_context(diff, ROWS, key_col="id", n=1)
    context_rows = [r for r in result if isinstance(r, ContextRow)]
    context_names = {r.row["name"] for r in context_rows}
    assert "Alice" in context_names
    assert "Carol" in context_names
