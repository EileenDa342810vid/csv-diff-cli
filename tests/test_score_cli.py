"""Unit tests for csv_diff.score_cli."""
import argparse
import pytest
from unittest.mock import patch
from csv_diff.score_cli import add_score_arguments, maybe_print_score
from csv_diff.diff import RowAdded


def _make_args(**kwargs):
    ns = argparse.Namespace(score=False, score_only=False)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_score_arguments_adds_flags():
    parser = argparse.ArgumentParser()
    add_score_arguments(parser)
    args = parser.parse_args(["--score"])
    assert args.score is True
    assert args.score_only is False


def test_no_flag_returns_false_prints_nothing(capsys):
    args = _make_args()
    result = maybe_print_score(args, [], 5)
    assert result is False
    assert capsys.readouterr().out == ""


def test_score_flag_prints_score(capsys):
    args = _make_args(score=True)
    result = maybe_print_score(args, [], 10)
    assert result is False
    out = capsys.readouterr().out
    assert "Score" in out


def test_score_only_returns_true(capsys):
    args = _make_args(score_only=True)
    result = maybe_print_score(args, [], 10)
    assert result is True


def test_score_only_suppresses_diff_in_caller(capsys):
    """Caller should suppress diff when maybe_print_score returns True."""
    args = _make_args(score_only=True)
    diff = [RowAdded(row={"id": "1"})]
    result = maybe_print_score(args, diff, 5)
    assert result is True
