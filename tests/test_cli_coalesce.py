"""Integration tests for the --coalesce CLI flag."""

import csv
import io
import subprocess
import sys
import tempfile
import os
from pathlib import Path

import pytest


def _write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    _write_csv(a, [
        {"id": "1", "region": "North", "sales": "100"},
        {"id": "2", "region": "",      "sales": "200"},
        {"id": "3", "region": "",      "sales": "300"},
    ])
    _write_csv(b, [
        {"id": "1", "region": "North", "sales": "100"},
        {"id": "2", "region": "North", "sales": "200"},
        {"id": "3", "region": "North", "sales": "300"},
    ])
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_coalesce_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--coalesce", "region")
    # With coalesced regions the files become identical → exit 0
    assert result.returncode == 0


def test_without_coalesce_detects_diff(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id")
    assert result.returncode == 1


def test_coalesce_invalid_column_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--coalesce", "nonexistent")
    assert result.returncode == 2
