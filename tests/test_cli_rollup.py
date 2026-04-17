"""Integration tests for --rollup CLI flag."""
import json
import subprocess
import sys
import tempfile
import os
import pytest


def _write_csv(path, rows):
    with open(path, "w") as f:
        f.write("\n".join(rows) + "\n")


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, ["id,name,amount", "1,Alice,100", "2,Bob,200"])
    _write_csv(b, ["id,name,amount", "1,Alice,150", "3,Carol,300"])
    return str(a), str(b)


def _run(a, b, *extra):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff.cli", a, b, *extra],
        capture_output=True, text=True
    )


def test_rollup_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--rollup", "amount")
    assert result.returncode in (0, 1)


def test_rollup_output_contains_column_header(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--rollup", "amount")
    assert "amount" in result.stdout


def test_rollup_invalid_column_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--rollup", "nonexistent")
    assert result.returncode == 2
