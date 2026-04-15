"""Integration tests for --save-baseline / --check-baseline CLI flags."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _write_csv(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, ["id,name", "1,Alice", "2,Bob"])
    _write_csv(b, ["id,name", "1,Alice", "3,Carol"])
    return a, b, tmp_path


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_save_baseline_creates_file(two_csvs):
    a, b, tmp = two_csvs
    baseline = tmp / "snap.json"
    result = _run(str(a), str(b), "--save-baseline", str(baseline))
    assert baseline.exists(), "baseline file should be created"
    data = json.loads(baseline.read_text())
    assert isinstance(data, list)
    assert len(data) > 0


def test_check_baseline_exits_zero_when_matching(two_csvs):
    a, b, tmp = two_csvs
    baseline = tmp / "snap.json"
    # First save
    _run(str(a), str(b), "--save-baseline", str(baseline))
    # Then check against the same pair
    result = _run(str(a), str(b), "--check-baseline", str(baseline))
    assert result.returncode == 0


def test_check_baseline_exits_nonzero_when_different(two_csvs, tmp_path):
    a, b, tmp = two_csvs
    baseline = tmp / "snap.json"
    _run(str(a), str(b), "--save-baseline", str(baseline))

    # Create a third CSV that differs from b
    c = tmp / "c.csv"
    _write_csv(c, ["id,name", "1,Alice", "2,Bob", "4,Dave"])
    result = _run(str(a), str(c), "--check-baseline", str(baseline))
    assert result.returncode != 0


def test_check_baseline_missing_file_exits_2(two_csvs):
    a, b, tmp = two_csvs
    result = _run(str(a), str(b), "--check-baseline", str(tmp / "nonexistent.json"))
    assert result.returncode == 2
    assert "baseline" in result.stderr.lower() or "baseline" in result.stdout.lower()
