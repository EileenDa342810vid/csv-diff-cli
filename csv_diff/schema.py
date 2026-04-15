"""Schema validation for CSV diff operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class SchemaError(Exception):
    """Raised when schema validation fails."""


@dataclass(frozen=True)
class ColumnSchema:
    """Describes the expected schema for a CSV file."""

    required_columns: tuple[str, ...]
    key_column: Optional[str] = None


def parse_required_columns(value: Optional[str]) -> Optional[tuple[str, ...]]:
    """Parse a comma-separated list of required column names.

    Returns None if *value* is None or an empty string.
    Raises SchemaError if any entry is blank after stripping.
    """
    if not value:
        return None
    parts = value.split(",")
    columns: list[str] = []
    for part in parts:
        stripped = part.strip()
        if not stripped:
            raise SchemaError(
                f"Invalid required-columns spec {value!r}: blank entry found."
            )
        columns.append(stripped)
    return tuple(columns)


def validate_schema(
    headers: list[str],
    schema: ColumnSchema,
) -> None:
    """Ensure *headers* satisfy *schema*.

    Raises SchemaError listing every missing column.
    """
    missing = [
        col for col in schema.required_columns if col not in headers
    ]
    if missing:
        raise SchemaError(
            "Required column(s) not found in CSV: "
            + ", ".join(repr(c) for c in missing)
        )
    if schema.key_column and schema.key_column not in headers:
        raise SchemaError(
            f"Key column {schema.key_column!r} not found in CSV headers."
        )


def describe_schema(schema: ColumnSchema) -> str:
    """Return a human-readable description of *schema*."""
    parts: list[str] = []
    if schema.required_columns:
        cols = ", ".join(schema.required_columns)
        parts.append(f"required columns: {cols}")
    if schema.key_column:
        parts.append(f"key column: {schema.key_column}")
    if not parts:
        return "(no constraints)"
    return "; ".join(parts)
