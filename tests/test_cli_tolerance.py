"""End-to-end CLI tests for --tolerance flag."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import os
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
    _write_csv(a, [{"id": "1", "price": "10.00"}, {"id": "2", "price": "20.00"}])
    _write_csv(b, [{"id": "1", "price": "10.03"}, {"id": "2", "price": "20.00"}])
    return a, b


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "csv_diff"] + args,
        capture_output=True,
        text=True,
    )


def test_tolerance_suppresses_small_diff(two_csvs):
    a, b = two_csvs
    result = _run([a, b, "--key", "id", "--tolerance", "price:0.05"])
    assert result.returncode == 0


def test_no_tolerance_detects_small_diff(two_csvs):
    a, b = two_csvs
    result = _run([a, b, "--key", "id"])
    assert result.returncode == 1


def test_tolerance_invalid_spec_exits_2(two_csvs):
    a, b = two_csvs
    result = _run([a, b, "--key", "id", "--tolerance", "badspec"])
    assert result.returncode == 2
