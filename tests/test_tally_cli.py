"""Unit tests for csv_diff.tally_cli."""
from __future__ import annotations

import argparse
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from csv_diff.diff import RowAdded
from csv_diff.tally_cli import add_tally_arguments, maybe_print_tally


def _make_args(**kwargs) -> argparse.Namespace:
    ns = argparse.Namespace(tally=None)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def _added(row):
    return RowAdded(row=row)


HEADERS = ["id", "region", "status"]


def test_add_tally_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_tally_arguments(parser)
    args = parser.parse_args(["--tally", "region"])
    assert args.tally == "region"


def test_no_flag_returns_false_prints_nothing(capsys):
    args = _make_args(tally=None)
    result = maybe_print_tally(args, [], HEADERS)
    assert result is False
    captured = capsys.readouterr()
    assert captured.out == ""


def test_tally_flag_returns_true_and_prints(capsys):
    args = _make_args(tally="region")
    events = [_added({"id": "1", "region": "North", "status": "active"})]
    result = maybe_print_tally(args, events, HEADERS)
    assert result is True
    captured = capsys.readouterr()
    assert "region" in captured.out
    assert "North" in captured.out


def test_invalid_column_exits_2(capsys):
    args = _make_args(tally="nonexistent")
    with pytest.raises(SystemExit) as exc_info:
        maybe_print_tally(args, [], HEADERS)
    assert exc_info.value.code == 2


def test_bad_spec_exits_2(capsys):
    args = _make_args(tally="region,,status")
    with pytest.raises(SystemExit) as exc_info:
        maybe_print_tally(args, [], HEADERS)
    assert exc_info.value.code == 2
