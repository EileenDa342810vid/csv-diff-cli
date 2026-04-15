"""Baseline snapshot support: save and load a CSV diff baseline for regression comparisons."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from csv_diff.diff import RowAdded, RowRemoved, RowModified


class BaselineError(Exception):
    """Raised when a baseline operation fails."""


def parse_baseline_path(value: Optional[str]) -> Optional[Path]:
    """Return a Path for *value*, or None when *value* is None."""
    if value is None:
        return None
    return Path(value)


def _event_to_dict(event) -> dict:
    if isinstance(event, RowAdded):
        return {"type": "added", "row": event.row}
    if isinstance(event, RowRemoved):
        return {"type": "removed", "row": event.row}
    if isinstance(event, RowModified):
        return {"type": "modified", "old_row": event.old_row, "new_row": event.new_row}
    raise BaselineError(f"Unknown diff event type: {type(event)}")


def _dict_to_event(data: dict):
    kind = data.get("type")
    if kind == "added":
        return RowAdded(row=data["row"])
    if kind == "removed":
        return RowRemoved(row=data["row"])
    if kind == "modified":
        return RowModified(old_row=data["old_row"], new_row=data["new_row"])
    raise BaselineError(f"Unknown baseline event type: {kind!r}")


def save_baseline(diff: list, path: Path) -> None:
    """Serialise *diff* to a JSON file at *path*."""
    try:
        payload = [_event_to_dict(e) for e in diff]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        raise BaselineError(f"Cannot write baseline to {path}: {exc}") from exc


def load_baseline(path: Path) -> list:
    """Deserialise a baseline JSON file and return a list of diff events."""
    if not path.exists():
        raise BaselineError(f"Baseline file not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineError(f"Cannot read baseline from {path}: {exc}") from exc
    return [_dict_to_event(item) for item in raw]


def diff_matches_baseline(diff: list, baseline: list) -> bool:
    """Return True when *diff* is identical to *baseline*."""
    if len(diff) != len(baseline):
        return False
    return all(_event_to_dict(a) == _event_to_dict(b) for a, b in zip(diff, baseline))
