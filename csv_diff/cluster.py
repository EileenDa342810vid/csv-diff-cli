"""Group diff events into clusters based on key proximity.

A cluster is a run of changed rows whose keys are "close" to each other
(within *gap* rows in the original file).  This is useful for surfacing
regions of concentrated change rather than scattered individual edits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved

DiffEvent = RowAdded | RowRemoved | RowModified


class ClusterError(ValueError):
    """Raised when cluster parameters are invalid."""


@dataclass
class EventCluster:
    events: List[DiffEvent] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.events)

    @property
    def added(self) -> int:
        return sum(1 for e in self.events if isinstance(e, RowAdded))

    @property
    def removed(self) -> int:
        return sum(1 for e in self.events if isinstance(e, RowRemoved))

    @property
    def modified(self) -> int:
        return sum(1 for e in self.events if isinstance(e, RowModified))


def parse_cluster_gap(value: object) -> Optional[int]:
    """Return an integer gap size or *None* if *value* is None."""
    if value is None:
        return None
    try:
        gap = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ClusterError(f"cluster gap must be an integer, got {value!r}")
    if gap < 0:
        raise ClusterError(f"cluster gap must be >= 0, got {gap}")
    return gap


def cluster_diff(
    events: Sequence[DiffEvent],
    gap: int = 0,
) -> List[EventCluster]:
    """Partition *events* into clusters separated by gaps larger than *gap*.

    Events are assumed to arrive in the order they appear in the diff (i.e.
    already sorted by key position).  Two consecutive events belong to the
    same cluster when the number of unchanged rows between them is <= *gap*.
    Because we don't have line numbers here we use the list index as a
    proxy: events at indices *i* and *i+1* are always adjacent in the diff
    stream, so we simply group consecutive events and split only when the
    caller sets gap=0 (each event is its own cluster) or gap>=1 (all
    consecutive events merge into one cluster per contiguous run).

    For a richer proximity model, callers should pre-sort events and pass
    gap values derived from annotated line numbers.
    """
    if not events:
        return []

    clusters: List[EventCluster] = []
    current = EventCluster(events=[events[0]])

    for prev_idx, event in enumerate(events[1:], start=1):
        # With no line-number information we treat gap as a simple
        # "merge all consecutive events" toggle.
        if gap >= 1:
            current.events.append(event)
        else:
            clusters.append(current)
            current = EventCluster(events=[event])

    clusters.append(current)
    return clusters


def format_clusters(clusters: List[EventCluster]) -> str:
    """Return a human-readable summary of *clusters*."""
    if not clusters:
        return "No clusters."
    lines = [f"{'Cluster':>7}  {'Total':>5}  {'Added':>5}  {'Removed':>7}  {'Modified':>8}"]
    for i, c in enumerate(clusters, 1):
        lines.append(f"{i:>7}  {c.size:>5}  {c.added:>5}  {c.removed:>7}  {c.modified:>8}")
    return "\n".join(lines)
