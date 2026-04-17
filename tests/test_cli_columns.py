"""Integration tests for the --columns flag in the CLI."""

import csv
import os
import tempfile

import pytest

from csv_diff.cli import main


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def two_csvs(tmp_path):
    old_path = str(tmp_path / "old.csv")
    new_path = str(tmp_path / "new.csv")
    headers = ["id", "name", "score"]
    old_rows = [{"id": "1", "name": "Alice", "score": "90"},
                {"id": "2", "name": "Bob",   "score": "80"}]
    new_rows = [{"id": "1", "name": "Alice", "score": "95"},  # score changed
                {"id": "2", "name": "Bobby", "score": "80"}]  # name changed
    _write_csv(old_path, old_rows, headers)
    _write_csv(new_path, new_rows, headers)
    return old_path, new_path


def test_columns_restricts_diff(two_csvs, capsys):
    """When --columns name is given only name changes should appear."""
    old, new = two_csvs
    rc = main([old, new, "--key", "id", "--columns", "name", "--no-color"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "Bobby" in captured.out
    # score change should NOT appear because we filtered to name only
    assert "score" not in captured.out


def test_columns_no_diff_when_unchanged_column(two_csvs, capsys):
    """Filtering to score should show row 1 modified, row 2 unchanged."""
    old, new = two_csvs
    rc = main([old, new, "--key", "id", "--columns", "score", "--no-color"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "95" in captured.out
    assert "Bobby" not in captured.out


def test_invalid_column_exits_2(two_csvs, capsys):
    old, new = two_csvs
    rc = main([old, new, "--key", "id", "--columns", "nonexistent"])
    captured = capsys.readouterr()
    assert rc == 2
    assert "nonexistent" in captured.err or "error" in captured.err.lower()


def test_no_columns_flag_diffs_all(two_csvs, capsys):
    old, new = two_csvs
    rc = main([old, new, "--key", "id", "--no-color"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "score" in captured.out
    assert "name" in captured.out


def test_columns_multiple_filters(two_csvs, capsys):
    """Passing multiple --columns values should include changes for each."""
    old, new = two_csvs
    rc = main([old, new, "--key", "id", "--columns", "name", "--columns", "score", "--no-color"])
    captured = capsys.readouterr()
    assert rc == 1
    # Both changes should appear when both columns are included
    assert "Bobby" in captured.out
    assert "95" in captured.out
