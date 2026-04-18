"""Flatten nested diff events into a tabular list of change records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from csv_diff.diff import RowAdded, RowRemoved, RowModified


class FlattenError(Exception):
    """Raised when flattening fails."""


@dataclass
class FlatRecord:
    change_type: str  # 'added', 'removed', 'modified'
    key: str
    column: Optional[str]  # None for added/removed rows
    old_value: Optional[str]
    new_value: Optional[str]


def flatten_diff(events: list) -> List[FlatRecord]:
    """Convert diff events into a flat list of FlatRecord entries.

    Added/removed rows produce one record per column.
    Modified rows produce one record per changed column.
    """
    records: List[FlatRecord] = []

    for event in events:
        if isinstance(event, RowAdded):
            for col, val in event.row.items():
                records.append(
                    FlatRecord(
                        change_type="added",
                        key=_key(event.row),
                        column=col,
                        old_value=None,
                        new_value=val,
                    )
                )
        elif isinstance(event, RowRemoved):
            for col, val in event.row.items():
                records.append(
                    FlatRecord(
                        change_type="removed",
                        key=_key(event.row),
                        column=col,
                        old_value=val,
                        new_value=None,
                    )
                )
        elif isinstance(event, RowModified):
            for col in event.old_row:
                old_val = event.old_row.get(col)
                new_val = event.new_row.get(col)
                if old_val != new_val:
                    records.append(
                        FlatRecord(
                            change_type="modified",
                            key=_key(event.old_row),
                            column=col,
                            old_value=old_val,
                            new_value=new_val,
                        )
                    )
        else:
            raise FlattenError(f"Unknown event type: {type(event)}")

    return records


def format_flat_records(records: List[FlatRecord]) -> str:
    """Format flat records as a human-readable table."""
    if not records:
        return "(no changes)"
    lines = [f"{'TYPE':<10} {'KEY':<20} {'COLUMN':<20} {'OLD':<20} {'NEW':<20}"]
    lines.append("-" * 92)
    for r in records:
        lines.append(
            f"{r.change_type:<10} {r.key:<20} {(r.column or ''):<20}"
            f" {(r.old_value or ''):<20} {(r.new_value or ''):<20}"
        )
    return "\n".join(lines)


def _key(row: dict) -> str:
    first_val = next(iter(row.values()), "")
    return str(first_val)
