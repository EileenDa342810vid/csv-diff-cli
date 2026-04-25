"""Unit tests for csv_diff.correlation_cli."""
from __future__ import annotations

import argparse
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from csv_diff.correlation_cli import add_correlation_arguments, maybe_print_correlation
from csv_diff.diff import RowAdded, RowModified


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"correlate": None, "correlate_only": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _modified():
    return RowModified(key="k1", changes={"price": ("1", "2"), "qty": ("1", "2")})


def test_add_correlation_arguments_adds_flags():
    parser = argparse.ArgumentParser()
    add_correlation_arguments(parser)
    args = parser.parse_args(["--correlate", "price,qty", "--correlate-only"])
    assert args.correlate == "price,qty"
    assert args.correlate_only is True


def test_no_flag_returns_false_prints_nothing(capsys):
    args = _make_args()
    result = maybe_print_correlation(args, [_modified()], ["price", "qty"])
    assert result is False
    captured = capsys.readouterr()
    assert captured.out == ""


def test_correlate_flag_prints_report(capsys):
    args = _make_args(correlate="price,qty")
    result = maybe_print_correlation(args, [_modified()], ["price", "qty"])
    assert result is False
    captured = capsys.readouterr()
    assert "Correlation" in captured.out


def test_correlate_only_returns_true(capsys):
    args = _make_args(correlate_only=True)
    result = maybe_print_correlation(args, [_modified()], ["price", "qty"])
    assert result is True


def test_invalid_column_exits_2():
    args = _make_args(correlate="nonexistent")
    with pytest.raises(SystemExit) as exc_info:
        maybe_print_correlation(args, [_modified()], ["price", "qty"])
    assert exc_info.value.code == 2
