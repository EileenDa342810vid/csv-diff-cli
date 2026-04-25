"""Fingerprint a diff by hashing its contents for change detection and deduplication."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import List, Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class FingerprintError(Exception):
    """Raised when fingerprinting fails."""


@dataclass(frozen=True)
class DiffFingerprint:
    hex: str
    event_count: int

    def short(self, length: int = 8) -> str:
        """Return a short version of the hex digest."""
        return self.hex[:length]

    def __str__(self) -> str:  # pragma: no cover
        return self.hex


def _event_to_stable_dict(event: object) -> dict:
    """Convert a diff event to a stable, serialisable dict."""
    if isinstance(event, RowAdded):
        return {"type": "added", "row": event.row}
    if isinstance(event, RowRemoved):
        return {"type": "removed", "row": event.row}
    if isinstance(event, RowModified):
        return {"type": "modified", "old": event.old_row, "new": event.new_row}
    raise FingerprintError(f"Unknown event type: {type(event).__name__}")


def compute_fingerprint(
    events: List[object],
    algorithm: str = "sha256",
) -> DiffFingerprint:
    """Hash all diff events into a single fingerprint.

    Events are serialised in stable JSON order so the fingerprint is
    deterministic regardless of dict insertion order.
    """
    try:
        h = hashlib.new(algorithm)
    except ValueError as exc:
        raise FingerprintError(f"Unsupported hash algorithm: {algorithm!r}") from exc

    for event in events:
        payload = _event_to_stable_dict(event)
        chunk = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        h.update(chunk.encode())

    return DiffFingerprint(hex=h.hexdigest(), event_count=len(events))


def format_fingerprint(fp: Optional[DiffFingerprint]) -> str:
    """Return a human-readable fingerprint report."""
    if fp is None:
        return "Fingerprint: n/a"
    return (
        f"Fingerprint : {fp.hex}\n"
        f"Short       : {fp.short()}\n"
        f"Events      : {fp.event_count}"
    )
