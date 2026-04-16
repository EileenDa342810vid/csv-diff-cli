"""Integration tests for the --transform CLI flag."""

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
    _write_csv(b, [{"id": "1", "name": "alice"}, {"id": "2", "name": "bob"}])
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_transform_lower_makes_files_identical(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--transform", "name:lower")
    assert result.returncode == 0


def test_without_transform_detects_case_diff(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id")
    assert result.returncode != 0


def test_transform_invalid_column_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--transform", "nonexistent:lower")
    assert result.returncode == 2


def test_transform_unknown_function_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--transform", "name:reverse")
    assert result.returncode == 2
