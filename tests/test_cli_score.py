"""Integration tests for --score / --score-only CLI flags."""
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
    _write_csv(a, ["id,name", "1,Alice", "2,Bob"])
    _write_csv(b, ["id,name", "1,Alice", "2,Charlie"])
    return str(a), str(b)


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True, text=True,
    )


def test_score_flag_accepted(two_csvs):
    a, b = two_csvs
    r = _run(a, b, "--score")
    assert "Score" in r.stdout


def test_score_contains_grade(two_csvs):
    a, b = two_csvs
    r = _run(a, b, "--score")
    assert "Grade" in r.stdout


def test_score_only_suppresses_diff(two_csvs):
    a, b = two_csvs
    r = _run(a, b, "--score-only")
    assert "Score" in r.stdout
    assert "MODIFIED" not in r.stdout


def test_score_identical_files(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, ["id,name", "1,Alice"])
    _write_csv(b, ["id,name", "1,Alice"])
    r = _run(str(a), str(b), "--score")
    assert "100.00%" in r.stdout
