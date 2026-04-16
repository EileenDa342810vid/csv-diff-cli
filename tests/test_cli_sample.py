"""Integration tests for --sample-size / --sample-mode CLI flags."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import os
from pathlib import Path

import pytest


def _write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, [{"id": str(i), "val": "old"} for i in range(1, 6)])
    _write_csv(b, [{"id": str(i), "val": "new"} for i in range(1, 6)])
    return a, b


def _run(args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff"] + args,
        capture_output=True,
        text=True,
    )


def test_sample_size_limits_output(two_csvs):
    a, b = two_csvs
    result = _run([str(a), str(b), "--sample-size", "2"])
    # 5 modified rows but only 2 should appear
    modified_lines = [l for l in result.stdout.splitlines() if "~" in l]
    assert len(modified_lines) <= 2


def test_no_sample_shows_all(two_csvs):
    a, b = two_csvs
    result = _run([str(a), str(b)])
    modified_lines = [l for l in result.stdout.splitlines() if "~" in l]
    assert len(modified_lines) == 5


def test_sample_invalid_exits_nonzero(two_csvs):
    a, b = two_csvs
    result = _run([str(a), str(b), "--sample-size", "abc"])
    assert result.returncode != 0
