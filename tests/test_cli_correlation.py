"""Integration tests for --correlate / --correlate-only CLI flags."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import os

import pytest


def _write_csv(path: str, rows: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        fh.write("\n".join(rows) + "\n")


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    _write_csv(a, ["id,price,qty", "1,10,5", "2,20,8"])
    _write_csv(b, ["id,price,qty", "1,15,7", "2,20,8"])
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_correlate_flag_accepted(two_csvs):
    a, b = two_csvs
    proc = _run(a, b, "--key", "id", "--correlate", "price,qty")
    assert proc.returncode in (0, 1)


def test_correlate_output_contains_header(two_csvs):
    a, b = two_csvs
    proc = _run(a, b, "--key", "id", "--correlate", "price,qty")
    assert "Correlation" in proc.stdout


def test_correlate_only_suppresses_diff(two_csvs):
    a, b = two_csvs
    proc = _run(a, b, "--key", "id", "--correlate", "price,qty", "--correlate-only")
    assert "Correlation" in proc.stdout
    assert "MODIFIED" not in proc.stdout


def test_invalid_correlate_column_exits_2(two_csvs):
    a, b = two_csvs
    proc = _run(a, b, "--key", "id", "--correlate", "nonexistent")
    assert proc.returncode == 2
