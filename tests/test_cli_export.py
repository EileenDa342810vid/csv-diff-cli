"""Integration tests for the --export-format CLI flag."""
import json
import os
import subprocess
import sys
import tempfile
import pytest


def _write_csv(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


@pytest.fixture()
def two_csvs(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    _write_csv(a, "id,name\n1,Alice\n2,Bob\n")
    _write_csv(b, "id,name\n1,Alice\n2,Bobby\n3,Carol\n")
    return a, b


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "csv_diff", *args],
        capture_output=True,
        text=True,
    )


def test_export_json_output_is_valid_json(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--export-format", "json")
    payload = json.loads(result.stdout)
    assert "changes" in payload
    types = {c["type"] for c in payload["changes"]}
    assert "added" in types
    assert "modified" in types


def test_export_json_with_stats(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--export-format", "json", "--stats")
    payload = json.loads(result.stdout)
    assert "stats" in payload
    assert payload["stats"]["added"] == 1


def test_export_markdown_output_contains_table(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--export-format", "markdown")
    assert "|" in result.stdout
    assert "Modified" in result.stdout or "Added" in result.stdout


def test_export_invalid_format_exits_2(two_csvs):
    a, b = two_csvs
    result = _run(a, b, "--export-format", "xml")
    assert result.returncode == 2


def test_no_export_format_uses_default_text(two_csvs):
    a, b = two_csvs
    result = _run(a, b)
    # Default text output should not be JSON
    with pytest.raises(json.JSONDecodeError):
        json.loads(result.stdout)
