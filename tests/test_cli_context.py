"""Integration tests for the --context CLI flag."""
import subprocess
import sys
import csv
import io
import os
import tempfile
import pytest


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    fields = ["id", "name", "score"]
    old_rows = [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob", "score": "80"},
        {"id": "3", "name": "Carol", "score": "70"},
        {"id": "4", "name": "Dave", "score": "60"},
        {"id": "5", "name": "Eve", "score": "50"},
    ]
    new_rows = [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob", "score": "85"},  # modified
        {"id": "3", "name": "Carol", "score": "70"},
        {"id": "4", "name": "Dave", "score": "60"},
        {"id": "5", "name": "Eve", "score": "50"},
    ]
    _write_csv(str(old), old_rows, fields)
    _write_csv(str(new), new_rows, fields)
    return str(old), str(new)


def _run(args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff"] + args,
        capture_output=True,
        text=True,
    )


def test_context_flag_accepted(two_csvs):
    old, new = two_csvs
    result = _run([old, new, "--context", "1"])
    assert result.returncode in (0, 1)


def test_no_context_flag_still_works(two_csvs):
    old, new = two_csvs
    result = _run([old, new])
    assert result.returncode in (0, 1)
    assert "score" in result.stdout


def test_invalid_context_exits_2(two_csvs):
    old, new = two_csvs
    result = _run([old, new, "--context", "-3"])
    assert result.returncode == 2


def test_non_integer_context_exits_2(two_csvs):
    old, new = two_csvs
    result = _run([old, new, "--context", "abc"])
    assert result.returncode == 2
