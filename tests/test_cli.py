"""Tests for the csv-diff CLI entry point."""

import csv
import os
import tempfile

import pytest

from csv_diff.cli import main


def write_temp_csv(rows: list[dict], delimiter: str = ",") -> str:
    """Write rows to a named temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", newline="") as fh:
        if rows:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter=delimiter)
            writer.writeheader()
            writer.writerows(rows)
    return path


@pytest.fixture(autouse=True)
def _cleanup(tmp_files):
    yield
    for path in tmp_files:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


@pytest.fixture()
def tmp_files():
    return []


def make_files(rows_a, rows_b, tmp_files):
    a = write_temp_csv(rows_a)
    b = write_temp_csv(rows_b)
    tmp_files.extend([a, b])
    return a, b


def test_no_diff_exits_zero(tmp_files):
    rows = [{"id": "1", "name": "Alice"}]
    a, b = make_files(rows, rows, tmp_files)
    assert main([a, b]) == 0


def test_diff_detected_exits_one(tmp_files):
    a, b = make_files(
        [{"id": "1", "name": "Alice"}],
        [{"id": "1", "name": "Bob"}],
        tmp_files,
    )
    assert main([a, b]) == 1


def test_added_row_exits_one(tmp_files):
    a, b = make_files(
        [{"id": "1", "name": "Alice"}],
        [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}],
        tmp_files,
    )
    assert main([a, b]) == 1


def test_missing_file_exits_one(tmp_files, capsys):
    a = write_temp_csv([{"id": "1"}])
    tmp_files.append(a)
    result = main([a, "/nonexistent/path/file.csv"])
    assert result == 1
    captured = capsys.readouterr()
    assert "Error reading file" in captured.err


def test_custom_key_column(tmp_files):
    a, b = make_files(
        [{"code": "X1", "value": "10"}],
        [{"code": "X1", "value": "20"}],
        tmp_files,
    )
    assert main([a, b, "--key", "code"]) == 1


def test_no_color_flag_does_not_crash(tmp_files, capsys):
    rows = [{"id": "1", "name": "Alice"}]
    a, b = make_files(rows, rows, tmp_files)
    result = main([a, b, "--no-color"])
    assert result == 0
    captured = capsys.readouterr()
    assert "No differences found." in captured.out
