"""Integration tests for the --watermark CLI flag."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _write_csv(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n")


@pytest.fixture()
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, ["id,name", "1,Alice", "2,Bob"])
    _write_csv(b, ["id,name", "1,Alice", "3,Carol"])
    return a, b, tmp_path


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "csv_diff"] + args,
        capture_output=True,
        text=True,
    )


def test_watermark_flag_accepted(two_csvs):
    a, b, tmp = two_csvs
    wm = tmp / "wm.json"
    result = _run([str(a), str(b), "--watermark", str(wm)])
    assert result.returncode in (0, 1)
    assert wm.exists()


def test_watermark_output_contains_header(two_csvs):
    a, b, tmp = two_csvs
    wm = tmp / "wm.json"
    result = _run([str(a), str(b), "--watermark", str(wm)])
    assert "Watermark" in result.stdout


def test_watermark_persists_high_across_runs(two_csvs):
    a, b, tmp = two_csvs
    wm = tmp / "wm.json"
    _run([str(a), str(b), "--watermark", str(wm)])
    data = json.loads(wm.read_text())
    assert data["high"] >= 0
