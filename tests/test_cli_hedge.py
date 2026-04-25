"""Integration tests for the --hedge CLI flag."""
import subprocess
import sys
import tempfile
import os

import pytest


def _write_csv(path: str, rows: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        fh.write("\n".join(rows) + "\n")


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    _write_csv(a, ["id,name,price", "1,apple,80", "2,banana,50"])
    _write_csv(b, ["id,name,price", "1,apple,120", "2,banana,60"])
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_hedge_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--hedge", "price:100")
    assert result.returncode in (0, 1)


def test_hedge_output_contains_crossing(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--hedge", "price:100")
    assert "price" in result.stdout
    assert "80" in result.stdout or "120" in result.stdout


def test_hedge_no_crossing_shows_clean_message(two_csvs):
    a, b = two_csvs
    # threshold of 200 means neither 80->120 nor 50->60 crosses it
    result = _run(a, b, "--key", "id", "--hedge", "price:200")
    assert "no threshold crossings" in result.stdout


def test_hedge_invalid_spec_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--hedge", "badspec")
    assert result.returncode == 2


def test_hedge_unknown_column_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--hedge", "nonexistent:100")
    assert result.returncode == 2
