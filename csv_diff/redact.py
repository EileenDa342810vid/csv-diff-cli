"""Redact (mask) specified column values in diff output."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved

_MASK = "***"


class RedactError(ValueError):
    pass


@dataclass
class RedactConfig:
    columns: list[str]


def parse_redact_columns(value: Optional[str]) -> Optional[RedactConfig]:
    """Parse a comma-separated list of column names to redact."""
    if not value or not value.strip():
        return None
    cols = [c.strip() for c in value.split(",")]
    empty = [c for c in cols if not c]
    if empty:
        raise RedactError("Redact column list contains empty entries.")
    return RedactConfig(columns=cols)


def validate_redact_columns(config: RedactConfig, headers: list[str]) -> None:
    """Raise RedactError if any redact column is not in headers."""
    missing = [c for c in config.columns if c not in headers]
    if missing:
        raise RedactError(f"Unknown redact columns: {', '.join(missing)}")


def _mask_row(row: dict[str, str], columns: list[str]) -> dict[str, str]:
    return {k: (_MASK if k in columns else v) for k, v in row.items()}


def redact_event(event: object, config: RedactConfig) -> object:
    """Return a copy of the event with specified columns masked."""
    cols = config.columns
    if isinstance(event, RowAdded):
        return RowAdded(key=event.key, row=_mask_row(event.row, cols))
    if isinstance(event, RowRemoved):
        return RowRemoved(key=event.key, row=_mask_row(event.row, cols))
    if isinstance(event, RowModified):
        return RowModified(
            key=event.key,
            before=_mask_row(event.before, cols),
            after=_mask_row(event.after, cols),
        )
    return event


def redact_diff(
    events: list, config: Optional[RedactConfig]
) -> list:
    """Apply redaction to every event in the diff list."""
    if config is None:
        return events
    return [redact_event(e, config) for e in events]
