"""Integration tests for the --stats CLI flag."""
from __future__ import annotations

import csv
import os
import tempfile
from typing import Generator

import pytest

from csv_diff.cli import main


def _write_csv(path: str, rows: list[dict]) -> None:
    if not rows:
        return
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs() -> Generator[tuple[str, str], None, None]:
    fa = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    fb = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    fa.close()
    fb.close()
    yield fa.name, fb.name
    os.unlink(fa.name)
    os.unlink(fb.name)


def test_stats_flag_no_changes(two_csvs, capsys):
    a, b = two_csvs
    rows = [{"id": "1", "name": "Alice"}]
    _write_csv(a, rows)
    _write_csv(b, rows)
    rc = main([a, b, "--stats"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "No differences" in captured.out


def test_stats_flag_with_added_row(two_csvs, capsys):
    a, b = two_csvs
    _write_csv(a, [{"id": "1", "name": "Alice"}])
    _write_csv(b, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    rc = main([a, b, "--stats"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "Added rows   : 1" in captured.out


def test_stats_flag_with_modified_row(two_csvs, capsys):
    a, b = two_csvs
    _write_csv(a, [{"id": "1", "name": "Alice"}])
    _write_csv(b, [{"id": "1", "name": "Alicia"}])
    rc = main([a, b, "--stats"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "Modified rows: 1" in captured.out
    assert "name: 1 change" in captured.out


def test_stats_not_printed_without_flag(two_csvs, capsys):
    a, b = two_csvs
    rows = [{"id": "1", "name": "Alice"}]
    _write_csv(a, rows)
    _write_csv(b, rows)
    main([a, b])
    captured = capsys.readouterr()
    assert "Diff Summary" not in captured.out


def test_stats_removed_row(two_csvs, capsys):
    a, b = two_csvs
    _write_csv(a, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    _write_csv(b, [{"id": "1", "name": "Alice"}])
    rc = main([a, b, "--stats"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "Removed rows : 1" in captured.out
