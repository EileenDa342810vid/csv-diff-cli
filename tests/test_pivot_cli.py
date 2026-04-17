"""Tests for csv_diff.pivot_cli."""
from __future__ import annotations

import argparse
import sys
import pytest

from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.pivot_cli import add_pivot_arguments, maybe_print_pivot


HEADERS = ["id", "region", "value"]


def _added(row):
    return RowAdded(row=row)


def _removed(row):
    return RowRemoved(row=row)


def _modified(old, new):
    return RowModified(old_row=old, new_row=new)


def _make_args(**kwargs):
    ns = argparse.Namespace(pivot_by=None)
    ns.__dict__.update(kwargs)
    return ns


def test_add_pivot_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_pivot_arguments(parser)
    args = parser.parse_args(["--pivot-by", "region"])
    assert args.pivot_by == "region"


def test_no_flag_returns_false_prints_nothing(capsys):
    diff = [_added({"id": "1", "region": "north", "value": "10"})]
    result = maybe_print_pivot(_make_args(), diff, HEADERS)
    assert result is False
    assert capsys.readouterr().out == ""


def test_pivot_flag_returns_true_and_prints(capsys):
    diff = [
        _added({"id": "1", "region": "north", "value": "10"}),
        _removed({"id": "2", "region": "south", "value": "20"}),
        _modified(
            {"id": "3", "region": "north", "value": "5"},
            {"id": "3", "region": "north", "value": "9"},
        ),
    ]
    result = maybe_print_pivot(_make_args(pivot_by="region"), diff, HEADERS)
    assert result is True
    out = capsys.readouterr().out
    assert "north" in out
    assert "south" in out


def test_pivot_invalid_column_exits_2(capsys):
    diff = [_added({"id": "1", "region": "north", "value": "10"})]
    with pytest.raises(SystemExit) as exc_info:
        maybe_print_pivot(_make_args(pivot_by="missing"), diff, HEADERS)
    assert exc_info.value.code == 2


def test_pivot_empty_diff_prints_no_changes(capsys):
    result = maybe_print_pivot(_make_args(pivot_by="region"), [], HEADERS)
    assert result is True
    assert "(no changes)" in capsys.readouterr().out
