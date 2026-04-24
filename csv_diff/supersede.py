"""supersede.py – mark diff events as superseded by a newer baseline.

A 'supersede' operation filters out diff events whose key values were
already present in a previously saved baseline, so repeat runs only
report genuinely new changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class SupersedeError(ValueError):
    """Raised when the supersede file cannot be parsed."""


@dataclass(frozen=True)
class SupersedeResult:
    kept: list
    dropped: int


def parse_supersede_path(value: Optional[str]) -> Optional[Path]:
    """Return a Path for *value*, or None when *value* is None / empty."""
    if not value:
        return None
    return Path(value)


def _event_key(event) -> Optional[str]:
    """Return the key value for an event, or None if unavailable."""
    row = None
    if isinstance(event, RowAdded):
        row = event.row
    elif isinstance(event, RowRemoved):
        row = event.row
    elif isinstance(event, RowModified):
        row = event.old_row
    if row is None:
        return None
    # Use the first column value as the key identifier
    return next(iter(row.values()), None)


def load_supersede_keys(path: Path) -> Set[str]:
    """Load the set of key values from a plain-text supersede file.

    Each non-empty line is treated as one key value.
    Raises SupersedeError on I/O problems.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise SupersedeError(f"Cannot read supersede file '{path}': {exc}") from exc
    return {line.strip() for line in lines if line.strip()}


def save_supersede_keys(path: Path, events: list) -> None:
    """Persist the key values from *events* to *path*."""
    keys = sorted({k for e in events if (k := _event_key(e)) is not None})
    path.write_text("\n".join(keys) + ("\n" if keys else ""), encoding="utf-8")


def apply_supersede(events: list, known_keys: Set[str]) -> SupersedeResult:
    """Remove events whose key already appears in *known_keys*.

    Returns a SupersedeResult with the surviving events and a count of
    how many were dropped.
    """
    kept = []
    dropped = 0
    for event in events:
        key = _event_key(event)
        if key is not None and key in known_keys:
            dropped += 1
        else:
            kept.append(event)
    return SupersedeResult(kept=kept, dropped=dropped)
