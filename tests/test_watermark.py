"""Unit tests for csv_diff.watermark."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from csv_diff.watermark import (
    WatermarkError,
    Watermark,
    check_watermark,
    format_watermark,
    load_watermark,
    parse_watermark_path,
    save_watermark,
)


def test_parse_watermark_path_none_returns_none():
    assert parse_watermark_path(None) is None


def test_parse_watermark_path_empty_returns_none():
    assert parse_watermark_path("") is None


def test_parse_watermark_path_returns_path():
    result = parse_watermark_path("/tmp/wm.json")
    assert result == Path("/tmp/wm.json")


def test_load_watermark_missing_file_returns_zero(tmp_path):
    assert load_watermark(tmp_path / "missing.json") == 0


def test_load_watermark_reads_stored_value(tmp_path):
    p = tmp_path / "wm.json"
    p.write_text(json.dumps({"high": 42}))
    assert load_watermark(p) == 42


def test_load_watermark_raises_on_corrupt_file(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not-json")
    with pytest.raises(WatermarkError):
        load_watermark(p)


def test_save_and_load_round_trip(tmp_path):
    p = tmp_path / "wm.json"
    save_watermark(p, 7)
    assert load_watermark(p) == 7


def test_check_watermark_updates_when_higher(tmp_path):
    p = tmp_path / "wm.json"
    save_watermark(p, 3)
    wm = check_watermark(p, 10)
    assert wm.previous == 3
    assert wm.current == 10
    assert wm.is_new_high is True
    assert load_watermark(p) == 10


def test_check_watermark_does_not_update_when_lower(tmp_path):
    p = tmp_path / "wm.json"
    save_watermark(p, 20)
    wm = check_watermark(p, 5)
    assert wm.is_new_high is False
    assert load_watermark(p) == 20


def test_format_watermark_new_high():
    wm = Watermark(path=Path("wm.json"), previous=2, current=9)
    text = format_watermark(wm)
    assert "NEW HIGH" in text
    assert "9" in text


def test_format_watermark_within_high():
    wm = Watermark(path=Path("wm.json"), previous=9, current=3)
    text = format_watermark(wm)
    assert "within previous high" in text
