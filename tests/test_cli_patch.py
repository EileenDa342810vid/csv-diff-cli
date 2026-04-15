"""Integration tests for --patch flag in the CLI."""

from __future__ import annotations

import csv
import io
import subprocess
import sys
import tempfile
import os
from pathlib import Path

import pytest


def _write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    _write_csv(a, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    _write_csv(b, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bobby"}])
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_patch_flag_accepted(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--patch", "unified")
    assert result.returncode in (0, 1)


def test_patch_output_contains_hunk_header(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--patch", "unified", "--no-color")
    assert "@@" in result.stdout


def test_patch_output_shows_modified_values(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--patch", "unified", "--no-color")
    assert "- name: Bob" in result.stdout
    assert "+ name: Bobby" in result.stdout


def test_invalid_patch_format_exits_nonzero(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--patch", "context")
    assert result.returncode == 2
