"""Integration tests for --pivot-by CLI flag."""
from __future__ import annotations

import csv
import io
import subprocess
import sys
import tempfile
import os
import pytest


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    _write_csv(
        a,
        [{"id": "1", "region": "north", "val": "10"},
         {"id": "2", "region": "south", "val": "20"}],
        ["id", "region", "val"],
    )
    _write_csv(
        b,
        [{"id": "1", "region": "north", "val": "99"},
         {"id": "3", "region": "east",  "val": "30"}],
        ["id", "region", "val"],
    )
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_pivot_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--pivot-by", "region")
    assert result.returncode in (0, 1)
    assert "Pivot by" in result.stdout


def test_pivot_output_contains_region_values(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--pivot-by", "region")
    assert "north" in result.stdout or "south" in result.stdout or "east" in result.stdout


def test_pivot_invalid_column_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--pivot-by", "nonexistent")
    assert result.returncode == 2
