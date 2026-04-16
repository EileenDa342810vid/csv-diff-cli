"""Integration tests for --rename flag via the CLI."""

import csv
import io
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
    _write_csv(a, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    _write_csv(b, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bobby"}])
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_rename_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--rename", "id=ID")
    # exit 1 because there is a diff, but no crash
    assert result.returncode in (0, 1)


def test_rename_invalid_spec_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--rename", "badspec")
    assert result.returncode == 2
    assert "error" in result.stderr


def test_rename_missing_column_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--rename", "nonexistent=X")
    assert result.returncode == 2
    assert "error" in result.stderr
