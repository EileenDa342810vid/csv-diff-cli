"""Unit tests for csv_diff.watermark_cli."""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import pytest

from csv_diff.watermark_cli import add_watermark_arguments, maybe_report_watermark


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"watermark": None, "watermark_fail_on_high": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_watermark_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_watermark_arguments(parser)
    args = parser.parse_args([])
    assert hasattr(args, "watermark")
    assert hasattr(args, "watermark_fail_on_high")


def test_no_flag_returns_none():
    args = _make_args(watermark=None)
    result = maybe_report_watermark(args, 5)
    assert result is None


def test_watermark_flag_prints_report(tmp_path):
    p = tmp_path / "wm.json"
    args = _make_args(watermark=str(p))
    out = io.StringIO()
    result = maybe_report_watermark(args, 3, file=out)
    assert result is True
    assert "Watermark" in out.getvalue()


def test_watermark_fail_on_high_exits_3(tmp_path):
    p = tmp_path / "wm.json"
    # previous high is 0, current is 5 — should trigger exit(3)
    args = _make_args(watermark=str(p), watermark_fail_on_high=True)
    out = io.StringIO()
    with pytest.raises(SystemExit) as exc_info:
        maybe_report_watermark(args, 5, file=out)
    assert exc_info.value.code == 3


def test_watermark_no_exit_when_not_new_high(tmp_path):
    p = tmp_path / "wm.json"
    p.write_text(json.dumps({"high": 99}))
    args = _make_args(watermark=str(p), watermark_fail_on_high=True)
    out = io.StringIO()
    # current (1) < previous (99) — must NOT exit
    result = maybe_report_watermark(args, 1, file=out)
    assert result is True
