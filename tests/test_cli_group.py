import subprocess
import sys
import csv
import tempfile
import os
import pytest


def _write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs( = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    _write_csv(a, [
        {"id": "1", "region": "EU", "value": "10"},
        {"id": "2", "region": "US", "value": "20"},
    ])
    _write_csv(b, [
        {"id": "1", "region": "EU", "value": "99"},
        {"id": "2", "region": "US", "value": "20"},
        {"id": "3", "region": "EU", "value": "30"},
    ])
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True, text=True,
    )


def test_group_by_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--group-by", "region")
    assert result.returncode in (0, 1)


def test_group_by_output_contains_region(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--group-by", "region")
    assert "region" in result.stdout


def test_group_by_invalid_column_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--group-by", "nosuchcol")
    assert result.returncode == 2


def test_group_by_shows_eu_and_us(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--group-by", "region")
    assert "EU" in result.stdout
    assert "US" in result.stdout
