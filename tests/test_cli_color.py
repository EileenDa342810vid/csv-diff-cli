"""Integration tests: --color / --no-color CLI flags."""

from __future__ import annotations

import csv
import io
import os
import tempfile
from pathlib import Path

import pytest

from csv_diff.cli import main


def _write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    _write_csv(b, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bobby"}])
    return str(a), str(b)


def test_no_color_flag_suppresses_ansi(two_csvs, capsys):
    a, b = two_csvs
    with pytest.raises(SystemExit):
        main([a, b, "--no-color"])
    out = capsys.readouterr().out
    assert "\033[" not in out


def test_color_flag_emits_ansi(two_csvs, capsys):
    a, b = two_csvs
    with pytest.raises(SystemExit):
        main([a, b, "--color"])
    out = capsys.readouterr().out
    assert "\033[" in out


def test_no_color_env_suppresses_ansi(two_csvs, capsys, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    a, b = two_csvs
    with pytest.raises(SystemExit):
        main([a, b])
    out = capsys.readouterr().out
    assert "\033[" not in out
