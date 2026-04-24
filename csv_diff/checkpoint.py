"""Checkpoint: save and compare named snapshots of diff results."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from csv_diff.diff import RowAdded, RowRemoved, RowModified


class CheckpointError(Exception):
    pass


@dataclass
class CheckpointMeta:
    name: str
    path: Path
    added: int
    removed: int
    modified: int

    @property
    def total(self) -> int:
        """Total number of changes across all event types."""
        return self.added + self.removed + self.modified


def parse_checkpoint_name(value: Optional[str]) -> Optional[str]:
    if not value or not value.strip():
        return None
    return value.strip()


def _events_to_dict(events: list) -> dict:
    added, removed, modified = 0, 0, 0
    for e in events:
        if isinstance(e, RowAdded):
            added += 1
        elif isinstance(e, RowRemoved):
            removed += 1
        elif isinstance(e, RowModified):
            modified += 1
    return {"added": added, "removed": removed, "modified": modified}


def save_checkpoint(name: str, events: list, directory: Path) -> CheckpointMeta:
    directory.mkdir(parents=True, exist_ok=True)
    safe = name.replace(" ", "_")
    path = directory / f"{safe}.json"
    data = {"name": name, **_events_to_dict(events)}
    path.write_text(json.dumps(data, indent=2))
    return CheckpointMeta(
        name=name,
        path=path,
        added=data["added"],
        removed=data["removed"],
        modified=data["modified"],
    )


def load_checkpoint(path: Path) -> CheckpointMeta:
    if not path.exists():
        raise CheckpointError(f"Checkpoint not found: {path}")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise CheckpointError(f"Invalid checkpoint file: {exc}") from exc
    return CheckpointMeta(
        name=data.get("name", path.stem),
        path=path,
        added=data.get("added", 0),
        removed=data.get("removed", 0),
        modified=data.get("modified", 0),
    )


def compare_checkpoints(a: CheckpointMeta, b: CheckpointMeta) -> List[str]:
    lines: List[str] = []
    for field in ("added", "removed", "modified"):
        va, vb = getattr(a, field), getattr(b, field)
        delta = vb - va
        sign = "+" if delta >= 0 else ""
        lines.append(f"  {field:10s}: {va} -> {vb}  ({sign}{delta})")
    return lines


def format_checkpoint(meta: CheckpointMeta) -> str:
    return (
        f"Checkpoint '{meta.name}'\n"
        f"  added:    {meta.added}\n"
        f"  removed:  {meta.removed}\n"
        f"  modified: {meta.modified}\n"
        f"  total:    {meta.total}"
    )
