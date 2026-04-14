"""Tests for csv_diff.reader module."""

import pytest
import csv
import tempfile
import os

from csv_diff.reader import read_csv, get_key_column, CSVReadError


def write_temp_csv(rows: list, headers: list, delimiter=",") -> str:
    """Helper to write a temporary CSV file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
    writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)
    f.close()
    return f.name


class TestReadCSV:
    def test_reads_basic_csv(self):
        path = write_temp_csv(
            [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}],
            headers=["id", "name"],
        )
        try:
            headers, rows = read_csv(path)
            assert headers == ["id", "name"]
            assert len(rows) == 2
            assert rows[0]["name"] == "Alice"
        finally:
            os.unlink(path)

    def test_reads_custom_delimiter(self):
        path = write_temp_csv(
            [{"id": "1", "val": "x"}],
            headers=["id", "val"],
            delimiter=";",
        )
        try:
            headers, rows = read_csv(path, delimiter=";")
            assert headers == ["id", "val"]
            assert rows[0]["val"] == "x"
        finally:
            os.unlink(path)

    def test_raises_on_missing_file(self):
        with pytest.raises(CSVReadError, match="File not found"):
            read_csv("/nonexistent/path/file.csv")

    def test_returns_empty_rows_for_header_only_csv(self):
        path = write_temp_csv([], headers=["id", "name"])
        try:
            headers, rows = read_csv(path)
            assert headers == ["id", "name"]
            assert rows == []
        finally:
            os.unlink(path)


class TestGetKeyColumn:
    def test_returns_first_column_by_default(self):
        assert get_key_column(["id", "name", "age"]) == "id"

    def test_returns_specified_key(self):
        assert get_key_column(["id", "name"], key="name") == "name"

    def test_raises_on_invalid_key(self):
        with pytest.raises(CSVReadError, match="Key column 'missing'"):
            get_key_column(["id", "name"], key="missing")

    def test_raises_on_empty_headers(self):
        with pytest.raises(CSVReadError, match="no columns"):
            get_key_column([])
