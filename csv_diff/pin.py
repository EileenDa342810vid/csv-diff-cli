"""Pin specific columns to always appear in diff output regardless of filter."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class PinError(Exception):
    pass


@dataclass
class PinConfig:
    columns: list[str] = field(default_factory=list)


def parse_pin_columns(value: Optional[str]) -> Optional[PinConfig]:
    """Parse a comma-separated list of column names to pin."""
    if not value or not value.strip():
        return None
    parts = [p.strip() for p in value.split(",")]
    for p in parts:
        if not p:
            raise PinError("Pin column entry must not be empty")
    return PinConfig(columns=parts)


def validate_pin_columns(config: Optional[PinConfig], headers: list[str]) -> None:
    """Raise PinError if any pinned column is not in headers."""
    if config is None:
        return
    missing = [c for c in config.columns if c not in headers]
    if missing:
        raise PinError(f"Pinned columns not found in headers: {', '.join(missing)}")


def apply_pin(row: dict[str, str], config: Optional[PinConfig], columns: Optional[list[str]]) -> dict[str, str]:
    """Merge pinned columns back into a filtered row dict.

    If *columns* is None (no filter active) the row is returned unchanged.
    Pinned columns that are already present are not duplicated.
    """
    if config is None or columns is None:
        return row
    result = dict(row)
    for col in config.columns:
        if col not in result and col in row:
            result[col] = row[col]
    return result


def merge_pin_columns(columns: Optional[list[str]], config: Optional[PinConfig]) -> Optional[list[str]]:
    """Return an extended column list that includes pinned columns.

    If *columns* is None the full set is already used, so None is returned.
    """
    if config is None or columns is None:
        return columns
    extra = [c for c in config.columns if c not in columns]
    return columns + extra
