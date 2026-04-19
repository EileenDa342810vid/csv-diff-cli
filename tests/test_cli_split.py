"""Integration tests for the --split CLI flag."""
import subprocess
import sys
import csv
import tempfile
import os


def _write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def two_csvs():
    a = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    b = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    a.close()
    b.close()
    _write_csv(a.name, [{"id": "1", "val": "x"}, {"id": "2", "val": "y"}])
    _write_csv(b.name, [{"id": "1", "val": "x"}, {"id": "3", "val": "z"}])
    return a.name, b.name


def _run(*args):
    a, b = two_csvs()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "csv_diff", a, b, "--key", "id"] + list(args),
            capture_output=True, text=True,
        )
        return result
    finally:
        os.unlink(a)
        os.unlink(b)


def test_split_flag_accepted():
    r = _run("--split")
    assert r.returncode in (0, 1)


def test_split_output_contains_summary():
    r = _run("--split")
    assert "Added" in r.stdout or "Added" in r.stderr


def test_no_split_flag_no_summary():
    r = _run()
    assert "Split Summary" not in r.stdout
