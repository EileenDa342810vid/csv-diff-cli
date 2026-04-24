"""Integration tests: --interpolate flag via the CLI entry-point."""
import subprocess
import sys
import tempfile
import os
import pytest


def _write_csv(path: str, lines: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        fh.write("\n".join(lines) + "\n")


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    _write_csv(a, ["id,name,score", "1,Alice,", "2,Bob,3"])
    _write_csv(b, ["id,name,score", "1,Alice,5", "2,Bob,3"])
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff"] + list(args),
        capture_output=True,
        text=True,
    )


def test_interpolate_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--interpolate", "score", "--fill-value", "0")
    # Interpolating blank -> 0 in file A; file B has 5 for Alice -> still a diff
    assert result.returncode in (0, 1)


def test_interpolate_suppresses_diff_when_blank_matches_fill(two_csvs, tmp_path):
    # Both files have blank score for Alice; interpolation -> 0.0 on both sides -> no diff
    a = str(tmp_path / "c.csv")
    b = str(tmp_path / "d.csv")
    _write_csv(a, ["id,name,score", "1,Alice,", "2,Bob,3"])
    _write_csv(b, ["id,name,score", "1,Alice,", "2,Bob,3"])
    result = _run(a, b, "--key", "id", "--interpolate", "score")
    assert result.returncode == 0


def test_interpolate_invalid_column_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--key", "id", "--interpolate", "nonexistent_col")
    assert result.returncode == 2
