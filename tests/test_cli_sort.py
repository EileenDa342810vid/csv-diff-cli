"""Integration tests for the --sort flag in the CLI."""

from __future__ import annotations

import csv
import os
import tempfile

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
def two_csvs(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(
        str(a),
        [
            {"id": "1", "name": "alice", "city": "NY"},
            {"id": "2", "name": "bob",   "city": "LA"},
            {"id": "3", "name": "carol", "city": "SF"},
        ],
    )
    _write_csv(
        str(b),
        [
            {"id": "1", "name": "alice", "city": "Boston"},  # modified city
            {"id": "2", "name": "robert", "city": "LA"},     # modified name
            {"id": "4", "name": "dave",  "city": "DC"},      # added
            # id=3 removed
        ],
    )
    return str(a), str(b)


def test_sort_key_exits_nonzero_on_changes(two_csvs, capsys):
    a, b = two_csvs
    rc = main([a, b, "--key", "id", "--sort", "key"])
    assert rc != 0


def test_sort_key_produces_output(two_csvs, capsys):
    a, b = two_csvs
    main([a, b, "--key", "id", "--sort", "key"])
    captured = capsys.readouterr()
    assert captured.out.strip() != ""


def test_sort_type_produces_output(two_csvs, capsys):
    a, b = two_csvs
    main([a, b, "--key", "id", "--sort", "type"])
    captured = capsys.readouterr()
    assert captured.out.strip() != ""


def test_sort_column_produces_output(two_csvs, capsys):
    a, b = two_csvs
    main([a, b, "--key", "id", "--sort", "column"])
    captured = capsys.readouterr()
    assert captured.out.strip() != ""


def test_invalid_sort_key_exits_2(two_csvs, capsys):
    a, b = two_csvs
    rc = main([a, b, "--key", "id", "--sort", "bogus"])
    assert rc == 2
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_no_sort_flag_works(two_csvs, capsys):
    a, b = two_csvs
    rc = main([a, b, "--key", "id"])
    assert rc != 0
    captured = capsys.readouterr()
    assert captured.out.strip() != ""
