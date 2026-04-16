"""Unit tests for csv_diff.rename_cli."""

import argparse
import sys

import pytest

from csv_diff.rename_cli import add_rename_arguments, resolve_renames


def _make_args(**kwargs) -> argparse.Namespace:
    ns = argparse.Namespace(rename=None)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_rename_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_rename_arguments(parser)
    args = parser.parse_args(["--rename", "a=A"])
    assert args.rename == "a=A"


def test_resolve_renames_none_returns_unchanged_headers():
    args = _make_args(rename=None)
    rename, headers = resolve_renames(args, ["id", "name"])
    assert rename is None
    assert headers == ["id", "name"]


def test_resolve_renames_returns_renamed_headers():
    args = _make_args(rename="id=ID")
    rename, headers = resolve_renames(args, ["id", "name"])
    assert headers == ["ID", "name"]
    assert rename is not None


def test_resolve_renames_exits_on_bad_spec(capsys):
    args = _make_args(rename="badspec")
    with pytest.raises(SystemExit) as exc_info:
        resolve_renames(args, ["id"])
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "error" in captured.err


def test_resolve_renames_exits_on_missing_column(capsys):
    args = _make_args(rename="missing=X")
    with pytest.raises(SystemExit) as exc_info:
        resolve_renames(args, ["id", "name"])
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "missing" in captured.err
