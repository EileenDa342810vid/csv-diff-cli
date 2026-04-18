"""Integration tests for the --drift CLI flag."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import os
from pathlib import Path

import pytest


def _write_csv(path: str, headers: list, rows: list) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    return a, b


def _run(a: str, b: str, extra: list = None):
    cmd = [sys.executable, "-m", "csv_diff", a, b] + (extra or [])
    return subprocess.run(cmd, capture_output=True, text=True)


def test_drift_flag_no_drift_exits_zero(two_csvs):
    a, b = two_csvs
    _write_csv(a, ["id", "name"], [["1", "Alice"]])
    _write_csv(b, ["id", "name"], [["1", "Alice"]])
    result = _run(a, b, ["--drift"])
    assert result.returncode == 0
    assert "No schema drift" in result.stdout


def test_drift_flag_added_column_exits_nonzero(two_csvs):
    a, b = two_csvs
    _write_csv(a, ["id", "name"], [["1", "Alice"]])
    _write_csv(b, ["id", "name", "email"], [["1", "Alice", "a@b.com"]])
    result = _run(a, b, ["--drift"])
    assert result.returncode != 0
    assert "email" in result.stdout


def test_drift_flag_removed_column_exits_nonzero(two_csvs):
    a, b = two_csvs
    _write_csv(a, ["id", "name", "score"], [["1", "Alice", "99"]])
    _write_csv(b, ["id", "name"], [["1", "Alice"]])
    result = _run(a, b, ["--drift"])
    assert result.returncode != 0
    assert "score" in result.stdout
