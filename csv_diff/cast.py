"""Type-casting utilities for CSV column values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


class CastError(Exception):
    """Raised when a cast specification is invalid."""


_SUPPORTED = {"int", "float", "str", "bool"}


@dataclass(frozen=True)
class ColumnCast:
    column: str
    type_name: str


def parse_casts(value: Optional[str]) -> Optional[List[ColumnCast]]:
    """Parse a comma-separated list of col:type specs.

    Returns None when *value* is None or empty.
    """
    if not value:
        return None
    casts: List[ColumnCast] = []
    for part in value.split(","):
        part = part.strip()
        if ":" not in part:
            raise CastError(f"Invalid cast spec {part!r}: expected 'column:type'")
        col, _, type_name = part.partition(":")
        col = col.strip()
        type_name = type_name.strip().lower()
        if not col:
            raise CastError(f"Empty column name in cast spec {part!r}")
        if type_name not in _SUPPORTED:
            raise CastError(
                f"Unsupported type {type_name!r} in {part!r}; "
                f"choose from {sorted(_SUPPORTED)}"
            )
        casts.append(ColumnCast(column=col, type_name=type_name))
    return casts or None


def validate_casts(casts: List[ColumnCast], headers: List[str]) -> None:
    """Raise CastError if any cast column is not present in *headers*."""
    header_set = set(headers)
    for cast in casts:
        if cast.column not in header_set:
            raise CastError(
                f"Cast column {cast.column!r} not found in headers: {headers}"
            )


def _cast_value(value: str, type_name: str) -> str:
    """Apply the cast and return the string representation."""
    try:
        if type_name == "int":
            return str(int(float(value)))
        if type_name == "float":
            return str(float(value))
        if type_name == "bool":
            return str(value.strip().lower() in {"1", "true", "yes"})
        return str(value)
    except (ValueError, TypeError) as exc:
        raise CastError(f"Cannot cast {value!r} to {type_name}: {exc}") from exc


def apply_casts(row: Dict[str, str], casts: List[ColumnCast]) -> Dict[str, str]:
    """Return a new row dict with cast columns replaced."""
    result = dict(row)
    for cast in casts:
        if cast.column in result:
            result[cast.column] = _cast_value(result[cast.column], cast.type_name)
    return result


def cast_rows(
    rows: List[Dict[str, str]], casts: Optional[List[ColumnCast]]
) -> List[Dict[str, str]]:
    """Apply *casts* to every row; returns rows unchanged when casts is None."""
    if not casts:
        return rows
    return [apply_casts(row, casts) for row in rows]
