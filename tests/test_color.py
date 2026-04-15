"""Tests for csv_diff.color."""

from __future__ import annotations

import pytest

from csv_diff.color import added, colorize, header, modified, removed


# ---------------------------------------------------------------------------
# colorize
# ---------------------------------------------------------------------------

def test_colorize_force_false_returns_plain():
    assert colorize("hello", "red", force=False) == "hello"


def test_colorize_force_true_wraps_text():
    result = colorize("hello", "red", force=True)
    assert result.startswith("\033[")
    assert "hello" in result
    assert result.endswith("\033[0m")


def test_colorize_unknown_colour_returns_plain():
    result = colorize("hello", "ultraviolet", force=True)
    assert result == "hello"


def test_colorize_no_color_env_disables(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert colorize("hi", "green") == "hi"


# ---------------------------------------------------------------------------
# Semantic helpers
# ---------------------------------------------------------------------------

def test_added_contains_green_code():
    result = added("+ row", force=True)
    assert "\033[32m" in result


def test_removed_contains_red_code():
    result = removed("- row", force=True)
    assert "\033[31m" in result


def test_modified_contains_yellow_code():
    result = modified("~ row", force=True)
    assert "\033[33m" in result


def test_header_contains_bold_and_cyan():
    result = header("=== Summary ===", force=True)
    assert "\033[1m" in result
    assert "\033[36m" in result


def test_added_plain_when_force_false():
    assert added("text", force=False) == "text"


def test_removed_plain_when_force_false():
    assert removed("text", force=False) == "text"


def test_header_plain_when_force_false():
    assert header("text", force=False) == "text"
