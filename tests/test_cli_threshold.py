import subprocess
import sys
import csv
import tempfile
import os
import pytest


def _write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    _write_csv(b, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Charlie"}, {"id": "3", "name": "Dave"}])
    return str(a), str(b)


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff"] + list(args),
        capture_output=True, text=True
    )


def test_threshold_below_suppresses_output(two_csvs):
    a, b = two_csvs
    r = _run(a, b, "--key", "id", "--threshold", "10")
    assert r.returncode == 0
    assert "suppressed" in r.stdout


def test_threshold_met_shows_diff(two_csvs):
    a, b = two_csvs
    r = _run(a, b, "--key", "id", "--threshold", "1")
    assert r.returncode == 1
    assert "suppressed" not in r.stdout


def test_invalid_threshold_exits_2(two_csvs):
    a, b = two_csvs
    r = _run(a, b, "--key", "id", "--threshold", "xyz")
    assert r.returncode == 2
