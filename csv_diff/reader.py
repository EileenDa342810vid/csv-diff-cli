"""CSV file reading and parsing utilities."""

import csv
from pathlib import Path
from typing import List, Dict, Optional


class CSVReadError(Exception):
    """Raised when a CSV file cannot be read or parsed."""
    pass


def read_csv(filepath: str, delimiter: str = ",") -> tuple[List[str], List[Dict[str, str]]]:
    """
    Read a CSV file and return its headers and rows.

    Args:
        filepath: Path to the CSV file.
        delimiter: Column delimiter character (default: comma).

    Returns:
        A tuple of (headers, rows) where rows is a list of dicts.

    Raises:
        CSVReadError: If the file does not exist or cannot be parsed.
    """
    path = Path(filepath)
    if not path.exists():
        raise CSVReadError(f"File not found: {filepath}")
    if not path.is_file():
        raise CSVReadError(f"Path is not a file: {filepath}")

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            if reader.fieldnames is None:
                raise CSVReadError(f"CSV file appears to be empty: {filepath}")
            headers = list(reader.fieldnames)
            rows = [dict(row) for row in reader]
    except csv.Error as e:
        raise CSVReadError(f"Failed to parse CSV file '{filepath}': {e}") from e
    except UnicodeDecodeError as e:
        raise CSVReadError(f"Encoding error reading '{filepath}': {e}") from e

    return headers, rows


def get_key_column(headers: List[str], key: Optional[str] = None) -> str:
    """
    Determine the key column to use for row matching.

    Args:
        headers: List of column headers.
        key: Explicitly specified key column name.

    Returns:
        The resolved key column name.

    Raises:
        CSVReadError: If the specified key is not found in headers.
    """
    if key is not None:
        if key not in headers:
            raise CSVReadError(
                f"Key column '{key}' not found. Available columns: {headers}"
            )
        return key
    if not headers:
        raise CSVReadError("CSV file has no columns.")
    return headers[0]
