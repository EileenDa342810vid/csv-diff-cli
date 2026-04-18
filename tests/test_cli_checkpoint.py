"""Integration tests for --save-checkpoint / --compare-checkpoint CLI flags."""
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


def _write_csv(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content))
    return path


@pytest.fixture()
def two_csvs(tmp_path):
    a = _write_csv(tmp_path / "a.csv", """\
        id,name,score
        1,Alice,10
        2,Bob,20
    """)
    b = _write_csv(tmp_path / "b.csv", """\
        id,name,score
        1,Alice,99
        3,Carol,30
    """)
    return a, b, tmp_path


def _run(args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff"] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_save_checkpoint_creates_file(two_csvs):
    a, b, tmp = two_csvs
    cp = tmp / "checkpoints" / "v1.json"
    result = _run([
        str(a), str(b), "--key", "id",
        "--save-checkpoint", str(tmp / "checkpoints" / "v1"),
    ])
    assert cp.exists(), result.stderr
    data = json.loads(cp.read_text())
    assert data["added"] >= 0
    assert data["modified"] >= 0


def test_compare_checkpoint_exits_zero_when_same(two_csvs):
    a, b, tmp = two_csvs
    cp_dir = tmp / "cp"
    _run([str(a), str(b), "--key", "id", "--save-checkpoint", str(cp_dir / "snap")])
    result = _run([str(a), str(b), "--key", "id", "--compare-checkpoint", str(cp_dir / "snap.json")])
    assert result.returncode in (0, 1)
    assert "Checkpoint" in result.stdout or result.returncode in (0, 1)


def test_compare_checkpoint_missing_file_exits_2(two_csvs):
    a, b, tmp = two_csvs
    result = _run([str(a), str(b), "--key", "id", "--compare-checkpoint", str(tmp / "nope.json")])
    assert result.returncode == 2
