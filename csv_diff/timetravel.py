"""Snapshot and replay support: save a timestamped snapshot of a diff and load it later."""

from __future__ import annotations

import json
import datetime
from pathlib import Path
from typing import List, Optional

from csv_diff.diff import RowAdded, RowRemoved, RowModified
from csv_diff.baseline import _event_to_dict, _dict_to_event


class TimeTravelError(Exception):
    pass


def parse_snapshot_path(value: Optional[str]) -> Optional[Path]:
    if not value:
        return None
    return Path(value)


def save_snapshot(events: list, path: Path) -> None:
    """Write events to a timestamped snapshot file."""
    try:
        payload = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "events": [_event_to_dict(e) for e in events],
        }
        path.write_text(json.dumps(payload, indent=2))
    except OSError as exc:
        raise TimeTravelError(f"Cannot write snapshot: {exc}") from exc


def load_snapshot(path: Path) -> tuple[str, list]:
    """Return (timestamp, events) from a snapshot file."""
    if not path.exists():
        raise TimeTravelError(f"Snapshot file not found: {path}")
    try:
        payload = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise TimeTravelError(f"Cannot read snapshot: {exc}") from exc
    timestamp = payload.get("timestamp", "unknown")
    events = [_dict_to_event(d) for d in payload.get("events", [])]
    return timestamp, events


def format_snapshot_header(timestamp: str, path: Path) -> str:
    return f"# Snapshot: {path.name}  (saved {timestamp})"
