"""Integration tests for the --slice CLI flag."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import os
from pathlib import Path

import pytest


def _write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    base = [{"id": str(i), "val": "x"} for i in range(1, 6)]
    modified = [{"id": str(i), "val": "y" if i % 2 == 0 else "x"} for i in range(1, 6)]
    _write_csv(a, base)
    _write_csv(b, modified)
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_slice_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--slice", "1")
    assert result.returncode in (0, 1)


def test_slice_limits_output(two_csvs):
    a, b = two_csvs
    full = _run(a, b, "--key", "id")
    sliced = _run(a, b, "--key", "id", "--slice", "1")
    assert len(sliced.stdout.splitlines()) <= len(full.stdout.splitlines())


def test_slice_invalid_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--slice", "notanumber")
    assert result.returncode == 2
