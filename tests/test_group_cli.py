import argparse
import pytest
from unittest.mock import patch
from csv_diff.group_cli import add_group_arguments, maybe_print_groups
from csv_diff.diff import RowAdded, RowRemoved


def _make_args(**kwargs):
    ns = argparse.Namespace(group_by=None)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_group_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_group_arguments(parser)
    args = parser.parse_args(["--group-by", "region"])
    assert args.group_by == "region"


def test_maybe_print_groups_returns_false_when_no_flag(capsys):
    args = _make_args(group_by=None)
    result = maybe_print_groups(args, [], ["id", "region"])
    assert result is False
    assert capsys.readouterr().out == ""


def test_maybe_print_groups_returns_true_and_prints(capsys):
    args = _make_args(group_by="region")
    events = [
        RowAdded(row={"id": "1", "region": "EU", "val": "x"}),
        RowRemoved(row={"id": "2", "region": "US", "val": "y"}),
    ]
    result = maybe_print_groups(args, events, ["id", "region", "val"])
    assert result is True
    out = capsys.readouterr().out
    assert "region" in out
    assert "EU" in out
    assert "US" in out


def test_maybe_print_groups_exits_on_bad_column():
    args = _make_args(group_by="nonexistent")
    with pytest.raises(SystemExit) as exc_info:
        maybe_print_groups(args, [], ["id", "region"])
    assert exc_info.value.code == 2


def test_maybe_print_groups_empty_events(capsys):
    args = _make_args(group_by="region")
    result = maybe_print_groups(args, [], ["id", "region"])
    assert result is True
    out = capsys.readouterr().out
    assert "No changes" in out
