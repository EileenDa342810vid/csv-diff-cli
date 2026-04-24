"""Unit tests for csv_diff.interpolate_cli."""
import argparse
import sys
import pytest

from csv_diff.interpolate_cli import add_interpolate_arguments, resolve_interpolate


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"interpolate": None, "fill_value": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_interpolate_arguments_adds_flags():
    parser = argparse.ArgumentParser()
    add_interpolate_arguments(parser)
    args = parser.parse_args(["--interpolate", "price", "--fill-value", "0"])
    assert args.interpolate == "price"
    assert args.fill_value == "0"


def test_resolve_interpolate_none_returns_rows_unchanged():
    rows = [{"a": "1"}, {"a": ""}]
    args = _make_args(interpolate=None)
    result = resolve_interpolate(args, ["a"], rows)
    assert result == rows


def test_resolve_interpolate_fills_blanks():
    rows = [{"price": ""}, {"price": "5"}]
    args = _make_args(interpolate="price", fill_value="0")
    result = resolve_interpolate(args, ["price"], rows)
    assert result[0]["price"] == "0.0"
    assert result[1]["price"] == "5"


def test_resolve_interpolate_exits_on_bad_column(capsys):
    rows = [{"price": ""}]
    args = _make_args(interpolate="nonexistent")
    with pytest.raises(SystemExit) as exc_info:
        resolve_interpolate(args, ["price"], rows)
    assert exc_info.value.code == 2


def test_resolve_interpolate_exits_on_bad_fill_value(capsys):
    rows = [{"price": ""}]
    args = _make_args(interpolate="price", fill_value="bad")
    with pytest.raises(SystemExit) as exc_info:
        resolve_interpolate(args, ["price"], rows)
    assert exc_info.value.code == 2
