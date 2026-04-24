"""Audit trail: attach a timestamp and run-id to each diff event."""
from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved

DiffEvent = RowAdded | RowRemoved | RowModified


class AuditError(ValueError):
    """Raised when audit configuration is invalid."""


@dataclass(frozen=True)
class AuditRecord:
    run_id: str
    timestamp: str  # ISO-8601
    event_type: str
    key: str
    detail: str


def generate_run_id() -> str:
    return str(uuid.uuid4())


def _event_type(event: DiffEvent) -> str:
    if isinstance(event, RowAdded):
        return "added"
    if isinstance(event, RowRemoved):
        return "removed"
    if isinstance(event, RowModified):
        return "modified"
    return "unknown"


def _event_detail(event: DiffEvent, key_column: str) -> str:
    if isinstance(event, RowAdded):
        return f"key={event.row.get(key_column, '?')}"
    if isinstance(event, RowRemoved):
        return f"key={event.row.get(key_column, '?')}"
    if isinstance(event, RowModified):
        changed = [c for c, (a, b) in event.changes.items() if a != b]
        return f"key={event.old_row.get(key_column, '?')} changed={','.join(changed)}"
    return ""


def audit_diff(
    events: Sequence[DiffEvent],
    key_column: str,
    run_id: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> List[AuditRecord]:
    """Wrap each diff event in an AuditRecord."""
    rid = run_id or generate_run_id()
    ts = timestamp or datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    records: List[AuditRecord] = []
    for event in events:
        key = (
            event.row.get(key_column, "?")
            if isinstance(event, (RowAdded, RowRemoved))
            else event.old_row.get(key_column, "?")
        )
        records.append(
            AuditRecord(
                run_id=rid,
                timestamp=ts,
                event_type=_event_type(event),
                key=key,
                detail=_event_detail(event, key_column),
            )
        )
    return records


def format_audit(records: List[AuditRecord]) -> str:
    """Return a human-readable audit log string."""
    if not records:
        return "Audit log: no changes recorded."
    lines = ["Audit log:", f"  run_id   : {records[0].run_id}"]
    for r in records:
        lines.append(f"  [{r.timestamp}] {r.event_type:10s} {r.detail}")
    return "\n".join(lines)
