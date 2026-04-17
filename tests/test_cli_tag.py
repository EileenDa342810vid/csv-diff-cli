"""Integration tests for --tag CLI flag."""

import subprocess
import sys
import tempfile
import os

import pytest


def _write_csv(path, rows):
    with open(path, "w") as f:
        for row in rows:
            f.write(row + "\n")


@pytest.fixture
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, ["id,status", "1,OK", "2,OK"])
    _write_csv(b, ["id,status", "1,FAIL", "2,OK"])
    return str(a), str(b)


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_tag_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--tag", "flag:status:FAIL")
    assert result.returncode in (0, 1)


def test_tag_output_contains_label(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--tag", "flag:status:FAIL")
    assert "flag" in result.stdout


def test_tag_invalid_spec_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--tag", "notvalid")
    assert result.returncode == 2
