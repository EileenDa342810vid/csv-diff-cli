"""Tests for csv_diff.compare_cli."""

import argparse
import pytest

from csv_diff.compare_cli import add_compare_arguments, resolve_tolerance


def _make_args(**kwargs) -> argparse.Namespace:
    ns = argparse.Namespace(tolerance=None)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_compare_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_compare_arguments(parser)
    args = parser.parse_args(["--tolerance", "price:0.01"])
    assert args.tolerance == "price:0.01"


def test_resolve_tolerance_none_returns_empty():
    args = _make_args(tolerance=None)
    result = resolve_tolerance(args, ["id", "price"])
    assert result == {}


def test_resolve_tolerance_returns_map():
    args = _make_args(tolerance="price:0.05")
    result = resolve_tolerance(args, ["id", "price"])
    assert result == {"price": 0.05}


def test_resolve_tolerance_exits_on_bad_spec(capsys):
    args = _make_args(tolerance="price")
    with pytest.raises(SystemExit) as exc_info:
        resolve_tolerance(args, ["id", "price"])
    assert exc_info.value.code == 2


def test_resolve_tolerance_exits_on_unknown_column(capsys):
    args = _make_args(tolerance="missing:0.01")
    with pytest.raises(SystemExit) as exc_info:
        resolve_tolerance(args, ["id", "price"])
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "missing" in captured.err
