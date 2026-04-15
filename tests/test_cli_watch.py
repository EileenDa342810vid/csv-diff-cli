"""CLI integration tests for --watch flag."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


def _write_csv(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content))


@pytest.fixture()
def two_csvs(tmp_path: Path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(a, """\
        id,name
        1,Alice
        2,Bob
    """)
    _write_csv(b, """\
        id,name
        1,Alice
        3,Carol
    """)
    return a, b


def _run(*args: str, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_watch_flag_help_text(two_csvs):
    """--help should mention the watch option."""
    result = _run("--help")
    assert result.returncode == 0
    assert "watch" in result.stdout.lower()


def test_watch_interval_invalid_exits_nonzero(two_csvs):
    """Passing a non-numeric interval should exit with an error."""
    a, b = two_csvs
    result = _run(str(a), str(b), "--watch", "--watch-interval", "fast")
    assert result.returncode != 0


def test_watch_missing_file_exits_nonzero(tmp_path: Path):
    """Watching a missing file should produce a non-zero exit code."""
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id\n1\n")
    # b intentionally not created
    result = _run(str(a), str(b), "--watch", "--watch-interval", "0.1")
    assert result.returncode != 0
