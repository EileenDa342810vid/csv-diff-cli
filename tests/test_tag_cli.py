"""Unit tests for csv_diff.tag_cli."""

import argparse
import sys
from types import SimpleNamespace

import pytest

from csv_diff.diff import RowAdded
from csv_diff.tag_cli import add_tag_arguments, resolve_tags


def _make_args(**kwargs):
    defaults = {"tag": None}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_add_tag_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_tag_arguments(parser)
    args = parser.parse_args(["--tag", "x:col:val"])
    assert args.tag == "x:col:val"


def test_resolve_tags_none_returns_wrapped_events():
    events = [RowAdded(row={"id": "1"})]
    args = _make_args(tag=None)
    result = resolve_tags(args, events)
    assert len(result) == 1
    assert result[0].tags == []


def test_resolve_tags_applies_rules():
    events = [RowAdded(row={"id": "1", "status": "FAIL"})]
    args = _make_args(tag="flag:status:FAIL")
    result = resolve_tags(args, events)
    assert "flag" in result[0].tags


def test_resolve_tags_exits_on_bad_spec(capsys):
    args = _make_args(tag="badspec")
    with pytest.raises(SystemExit) as exc_info:
        resolve_tags(args, [])
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "error" in captured.err
