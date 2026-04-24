"""Coalesce: fill empty values in a column using the previous non-empty value."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


class CoalesceError(ValueError):
    """Raised when coalesce configuration is invalid."""


@dataclass(frozen=True)
class CoalesceConfig:
    columns: List[str]


def parse_coalesce_columns(value: Optional[str]) -> Optional[CoalesceConfig]:
    """Parse a comma-separated list of column names to coalesce.

    Returns None if *value* is None or empty.
    """
    if not value or not value.strip():
        return None
    parts = [p.strip() for p in value.split(",")]
    for part in parts:
        if not part:
            raise CoalesceError(
                "Coalesce column list contains an empty entry; "
                "check for stray commas."
            )
    return CoalesceConfig(columns=parts)


def validate_coalesce_columns(
    config: CoalesceConfig, headers: List[str]
) -> None:
    """Raise CoalesceError if any column in *config* is not in *headers*."""
    missing = [c for c in config.columns if c not in headers]
    if missing:
        raise CoalesceError(
            f"Coalesce column(s) not found in headers: {', '.join(missing)}"
        )


def coalesce_rows(
    rows: List[Dict[str, str]],
    config: CoalesceConfig,
) -> List[Dict[str, str]]:
    """Return a new list of rows with empty values filled from the previous row.

    Only columns listed in *config.columns* are affected.  The fill propagates
    forward: once a non-empty value is seen it becomes the current fill value
    until a new non-empty value replaces it.
    """
    last: Dict[str, str] = {col: "" for col in config.columns}
    result: List[Dict[str, str]] = []
    for row in rows:
        new_row = dict(row)
        for col in config.columns:
            if new_row.get(col, "").strip() == "":
                new_row[col] = last[col]
            else:
                last[col] = new_row[col]
        result.append(new_row)
    return result
