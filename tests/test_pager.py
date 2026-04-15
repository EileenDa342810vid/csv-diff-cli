"""Tests for csv_diff.pager."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from csv_diff.pager import (
    PagerError,
    _detect_pager,
    page_output,
    should_page,
)


# ---------------------------------------------------------------------------
# _detect_pager
# ---------------------------------------------------------------------------

def test_detect_pager_uses_env_variable(monkeypatch):
    monkeypatch.setenv("CSV_DIFF_PAGER", "my-pager")
    assert _detect_pager() == "my-pager"


def test_detect_pager_falls_back_to_pager_env(monkeypatch):
    monkeypatch.delenv("CSV_DIFF_PAGER", raising=False)
    monkeypatch.setenv("PAGER", "pg")
    assert _detect_pager() == "pg"


def test_detect_pager_returns_less_when_available(monkeypatch):
    monkeypatch.delenv("CSV_DIFF_PAGER", raising=False)
    monkeypatch.delenv("PAGER", raising=False)
    with patch("csv_diff.pager.shutil.which", side_effect=lambda x: x if x == "less" else None):
        result = _detect_pager()
    assert result is not None and "less" in result


def test_detect_pager_returns_none_when_nothing_found(monkeypatch):
    monkeypatch.delenv("CSV_DIFF_PAGER", raising=False)
    monkeypatch.delenv("PAGER", raising=False)
    with patch("csv_diff.pager.shutil.which", return_value=None):
        assert _detect_pager() is None


# ---------------------------------------------------------------------------
# should_page
# ---------------------------------------------------------------------------

def test_should_page_force_true():
    assert should_page("x", force=True) is True


def test_should_page_force_false():
    assert should_page("\n" * 200, force=False) is False


def test_should_page_no_tty_returns_false():
    with patch.object(sys.stdout, "isatty", return_value=False):
        assert should_page("\n" * 200) is False


def test_should_page_tall_output_on_tty():
    with patch.object(sys.stdout, "isatty", return_value=True):
        with patch("csv_diff.pager.shutil.get_terminal_size", return_value=MagicMock(lines=24)):
            assert should_page("\n" * 30) is True


def test_should_page_short_output_on_tty():
    with patch.object(sys.stdout, "isatty", return_value=True):
        with patch("csv_diff.pager.shutil.get_terminal_size", return_value=MagicMock(lines=24)):
            assert should_page("hello") is False


# ---------------------------------------------------------------------------
# page_output
# ---------------------------------------------------------------------------

def test_page_output_no_pager_prints(capsys):
    page_output("hello world", pager_cmd="")
    captured = capsys.readouterr()
    assert "hello world" in captured.out


def test_page_output_calls_pager_subprocess():
    mock_proc = MagicMock()
    mock_proc.stdin = MagicMock()
    with patch("csv_diff.pager.subprocess.Popen", return_value=mock_proc) as mock_popen:
        page_output("some text", pager_cmd="less -R")
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        # The pager command should be passed as the first positional argument
        assert args[0] == "less -R" or (isinstance(args[0], list) and "less" in args[0][0])


def test_page_output_pager_receives_text():
    """Ensure the output text is actually written to the pager's stdin."""
    mock_proc = MagicMock()
    mock_proc.stdin = MagicMock()
    with patch("csv_diff.pager.subprocess.Popen", return_value=mock_proc):
        page_output("hello pager", pager_cmd="less")
        written = b"".join(
            call.args[0]
            for call in mock_proc.stdin.write.call_args_list
        )
        assert b"hello pager" in written
