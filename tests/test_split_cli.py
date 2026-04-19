"""Tests for csv_diff.split_cli."""
import argparse
from unittest.mock import patch
from csv_diff.split_cli import add_split_arguments, maybe_print_split
from csv_diff.diff import RowAdded, RowRemoved


def _make_args(**kwargs):
    ns = argparse.Namespace(split=False)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_split_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_split_arguments(parser)
    args = parser.parse_args(["--split"])
    assert args.split is True


def test_no_flag_returns_false_prints_nothing():
    args = _make_args(split=False)
    with patch("builtins.print") as mock_print:
        result = maybe_print_split(args, [])
    assert result is False
    mock_print.assert_not_called()


def test_split_flag_returns_true_and_prints():
    args = _make_args(split=True)
    events = [RowAdded(row={"id": "1"}), RowRemoved(row={"id": "2"})]
    with patch("builtins.print") as mock_print:
        result = maybe_print_split(args, events)
    assert result is True
    mock_print.assert_called_once()
    output = mock_print.call_args[0][0]
    assert "Added" in output
    assert "Removed" in output
