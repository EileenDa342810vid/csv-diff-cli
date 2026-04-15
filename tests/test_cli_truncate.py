"""Integration tests for the --max-width CLI flag."""

import subprocess
import sys
import os
import tempfile
import pytest


def _write_csv(path: str, content: str) -> None:
    with open(path, "w", newline="") as fh:
        fh.write(content)


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(
        str(a),
        "id,name,description\n"
        "1,Alice,Short\n"
        "2,Bob,A very long description that exceeds forty characters easily\n",
    )
    _write_csv(
        str(b),
        "id,name,description\n"
        "1,Alice,Short\n"
        "2,Bob,Updated: A very long description that exceeds forty characters easily\n",
    )
    return str(a), str(b)


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff.cli", *args],
        capture_output=True,
        text=True,
    )


def test_max_width_truncates_long_values(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--max-width", "20")
    # Output should contain ellipsis for the truncated long value
    assert "..." in result.stdout


def test_no_max_width_shows_full_values(two_csvs):
    a, b = two_csvs
    result = _run(a, b)
    assert "exceeds forty characters easily" in result.stdout


def test_max_width_invalid_value_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--max-width", "notanumber")
    assert result.returncode == 2


def test_max_width_zero_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--max-width", "0")
    assert result.returncode == 2
