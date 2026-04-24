"""Tests for csv_diff.dedupe_cli."""
from __future__ import annotations

import argparse
import pytest

from csv_diff.dedupe_cli import add_dedupe_arguments, maybe_report_duplicates


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"dedupe": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _rows(*keys: str) -> list:
    return [{"id": k, "val": "x"} for k in keys]


# ---------------------------------------------------------------------------
# add_dedupe_arguments
# ---------------------------------------------------------------------------

def test_add_dedupe_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_dedupe_arguments(parser)
    ns = parser.parse_args([])
    assert ns.dedupe is False


def test_add_dedupe_arguments_flag_sets_true():
    parser = argparse.ArgumentParser()
    add_dedupe_arguments(parser)
    ns = parser.parse_args(["--dedupe"])
    assert ns.dedupe is True


# ---------------------------------------------------------------------------
# maybe_report_duplicates – flag not set
# ---------------------------------------------------------------------------

def test_no_flag_returns_false(capsys):
    args = _make_args(dedupe=False)
    result = maybe_report_duplicates(args, _rows("1", "2"), _rows("1"), "id")
    assert result is False
    captured = capsys.readouterr()
    assert captured.out == ""


# ---------------------------------------------------------------------------
# maybe_report_duplicates – flag set, clean files
# ---------------------------------------------------------------------------

def test_clean_files_print_message_and_exit_zero(capsys):
    args = _make_args(dedupe=True)
    with pytest.raises(SystemExit) as exc_info:
        maybe_report_duplicates(args, _rows("1", "2"), _rows("3", "4"), "id")
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "No duplicate keys found" in out


# ---------------------------------------------------------------------------
# maybe_report_duplicates – flag set, duplicates present
# ---------------------------------------------------------------------------

def test_duplicates_exit_one(capsys):
    args = _make_args(dedupe=True)
    rows_with_dupes = _rows("1", "1", "2")
    with pytest.raises(SystemExit) as exc_info:
        maybe_report_duplicates(args, rows_with_dupes, _rows("3"), "id")
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "1" in out  # duplicate key appears in output


# ---------------------------------------------------------------------------
# maybe_report_duplicates – missing key column
# ---------------------------------------------------------------------------

def test_missing_key_column_exits_two(capsys):
    args = _make_args(dedupe=True)
    with pytest.raises(SystemExit) as exc_info:
        maybe_report_duplicates(args, [{"name": "alice"}], [], "id")
    assert exc_info.value.code == 2
    err = capsys.readouterr().err
    assert "dedupe error" in err
