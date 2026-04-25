"""Integration tests for the --velocity CLI flag."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import os
from pathlib import Path

import pytest


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, [{"id": "1", "name": "Alice", "score": "80"}], ["id", "name", "score"])
    _write_csv(b, [{"id": "1", "name": "Alice", "score": "95"}], ["id", "name", "score"])
    return a, b


def _run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_velocity_flag_accepted(two_csvs):
    a, b = two_csvs
    proc = _run(str(a), str(b), "--velocity")
    assert proc.returncode in (0, 1)


def test_velocity_output_contains_column_header(two_csvs):
    a, b = two_csvs
    proc = _run(str(a), str(b), "--velocity")
    assert "Velocity" in proc.stdout


def test_velocity_output_lists_score_column(two_csvs):
    a, b = two_csvs
    proc = _run(str(a), str(b), "--velocity")
    assert "score" in proc.stdout
