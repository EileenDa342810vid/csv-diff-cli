"""Quorum voting: given multiple diff lists, keep only events agreed upon by a
minimum number of sources (useful when comparing three or more CSV snapshots)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .diff import RowAdded, RowModified, RowRemoved

DiffEvent = RowAdded | RowRemoved | RowModified


class QuorumError(ValueError):
    """Raised when quorum arguments are invalid."""


@dataclass
class QuorumResult:
    events: List[DiffEvent] = field(default_factory=list)
    total_candidates: int = 0
    quorum_required: int = 1

    @property
    def accepted(self) -> int:
        return len(self.events)

    @property
    def rejected(self) -> int:
        return self.total_candidates - self.accepted


def parse_quorum(value: Optional[object]) -> Optional[int]:
    """Parse a quorum threshold from CLI input."""
    if value is None:
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise QuorumError(f"quorum must be an integer, got {value!r}")
    if n < 1:
        raise QuorumError(f"quorum must be >= 1, got {n}")
    return n


def _event_key(event: DiffEvent) -> Tuple[str, str]:
    """Return a (type, key_value) tuple for deduplication."""
    if isinstance(event, RowAdded):
        return ("added", str(event.row))
    if isinstance(event, RowRemoved):
        return ("removed", str(event.row))
    if isinstance(event, RowModified):
        return ("modified", str(event.old_row))
    return ("unknown", str(event))  # type: ignore[unreachable]


def quorum_diff(
    diff_lists: List[List[DiffEvent]],
    quorum: int = 1,
) -> QuorumResult:
    """Return only events that appear in at least *quorum* of the diff lists."""
    if quorum < 1:
        raise QuorumError(f"quorum must be >= 1, got {quorum}")
    if not diff_lists:
        return QuorumResult(quorum_required=quorum)

    counts: Dict[Tuple[str, str], int] = {}
    first_seen: Dict[Tuple[str, str], DiffEvent] = {}

    for diff in diff_lists:
        seen_in_this = set()
        for event in diff:
            k = _event_key(event)
            if k not in seen_in_this:
                counts[k] = counts.get(k, 0) + 1
                first_seen.setdefault(k, event)
                seen_in_this.add(k)

    accepted = [
        first_seen[k] for k, cnt in counts.items() if cnt >= quorum
    ]
    total = sum(len(d) for d in diff_lists)
    return QuorumResult(
        events=accepted,
        total_candidates=total,
        quorum_required=quorum,
    )


def format_quorum(result: QuorumResult) -> str:
    lines = [
        "=== Quorum Report ===",
        f"Required : {result.quorum_required}",
        f"Accepted : {result.accepted}",
        f"Rejected : {result.rejected}",
    ]
    return "\n".join(lines)
