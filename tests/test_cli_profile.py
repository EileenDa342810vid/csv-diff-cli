"""CLI integration tests for --profile flag."""
import json
import subprocess
import sys
import os
import tempfile
import pytest


def _write_csv(path, rows):
    with open(path, "w") as f:
        f.write("\n".join(rows) + "\n")


@pytest.fixture
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, ["id,name,score", "1,Alice,10", "2,Bob,20"])
    _write_csv(b, ["id,name,score", "1,Alice,30", "2,Bob,20", "3,Carol,50"])
    return str(a), str(b)


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True, text=True
    )


def test_profile_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--profile")
    assert result.returncode in (0, 1)


def test_profile_output_contains_column_header(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--profile")
    assert "Column" in result.stdout or "Column" in result.stderr


def test_profile_shows_changed_column(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--profile")
    combined = result.stdout + result.stderr
    assert "score" in combined


def test_profile_no_diff_still_runs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, ["id,name", "1,Alice"])
    _write_csv(b, ["id,name", "1,Alice"])
    result = _run(str(a), str(b), "--profile")
    assert result.returncode == 0
