"""Unit tests for csv_diff.velocity_cli."""

from __future__ import annotations

import argparse
import io
import sys

import pytest

from csv_diff.diff import RowModified
from csv_diff.velocity_cli import add_velocity_arguments, maybe_print_velocity


HEADERS = ["id", "name", "score"]


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"velocity": False, "velocity_only": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _modified(old: dict, new: dict) -> RowModified:
    return RowModified(old_row=old, new_row=new)


def test_add_velocity_arguments_adds_flags():
    parser = argparse.ArgumentParser()
    add_velocity_arguments(parser)
    args = parser.parse_args(["--velocity"])
    assert args.velocity is True
    assert args.velocity_only is False


def test_add_velocity_only_flag():
    parser = argparse.ArgumentParser()
    add_velocity_arguments(parser)
    args = parser.parse_args(["--velocity-only"])
    assert args.velocity_only is True


def test_no_flag_returns_false_prints_nothing(capsys):
    args = _make_args()
    result = maybe_print_velocity(args, [], HEADERS)
    assert result is False
    captured = capsys.readouterr()
    assert captured.out == ""


def test_velocity_flag_returns_false_and_prints(capsys):
    args = _make_args(velocity=True)
    result = maybe_print_velocity(args, [], HEADERS)
    assert result is False
    captured = capsys.readouterr()
    assert "Velocity" in captured.out


def test_velocity_only_flag_returns_true(capsys):
    args = _make_args(velocity_only=True)
    result = maybe_print_velocity(args, [], HEADERS)
    assert result is True


def test_velocity_output_contains_column_names(capsys):
    events = [
        _modified(
            {"id": "1", "name": "A", "score": "10"},
            {"id": "1", "name": "B", "score": "20"},
        )
    ]
    args = _make_args(velocity=True)
    maybe_print_velocity(args, events, HEADERS)
    captured = capsys.readouterr()
    for col in HEADERS:
        assert col in captured.out
