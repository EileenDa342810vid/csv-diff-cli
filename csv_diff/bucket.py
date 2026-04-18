"""Group diff events into named buckets based on a column's value ranges."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class BucketError(Exception):
    pass


@dataclass
class BucketResult:
    name: str
    added: int = 0
    removed: int = 0
    modified: int = 0

    @property
    def total(self) -> int:
        return self.added + self.removed + self.modified


def parse_bucket_column(value: Optional[str]) -> Optional[str]:
    if not value or not value.strip():
        return None
    return value.strip()


def parse_bucket_edges(value: Optional[str]) -> Optional[List[float]]:
    """Parse a comma-separated list of numeric edges, e.g. '0,100,500'."""
    if not value or not value.strip():
        return None
    parts = [p.strip() for p in value.split(",")]
    try:
        edges = [float(p) for p in parts]
    except ValueError as exc:
        raise BucketError(f"Bucket edges must be numeric: {exc}") from exc
    if edges != sorted(edges):
        raise BucketError("Bucket edges must be in ascending order.")
    return edges


def _bucket_name(value: str, edges: List[float]) -> str:
    try:
        num = float(value)
    except ValueError:
        return "other"
    for i, edge in enumerate(edges[1:], 1):
        if num < edge:
            lo = edges[i - 1]
            return f"{lo}-{edge}"
    return f">={edges[-1]}"


def bucket_diff(
    events: Sequence,
    column: str,
    edges: List[float],
) -> Dict[str, BucketResult]:
    results: Dict[str, BucketResult] = {}
    for event in events:
        if isinstance(event, RowAdded):
            row = event.row
            change = "added"
        elif isinstance(event, RowRemoved):
            row = event.row
            change = "removed"
        elif isinstance(event, RowModified):
            row = event.new_row
            change = "modified"
        else:
            continue
        if column not in row:
            raise BucketError(f"Column '{column}' not found in row.")
        name = _bucket_name(row[column], edges)
        if name not in results:
            results[name] = BucketResult(name=name)
        setattr(results[name], change, getattr(results[name], change) + 1)
    return results


def format_bucket_table(buckets: Dict[str, BucketResult]) -> str:
    if not buckets:
        return "No bucketed changes."
    lines = [f"{'Bucket':<20} {'Added':>6} {'Removed':>8} {'Modified':>9} {'Total':>6}"]
    lines.append("-" * 54)
    for name, b in sorted(buckets.items()):
        lines.append(f"{name:<20} {b.added:>6} {b.removed:>8} {b.modified:>9} {b.total:>6}")
    return "\n".join(lines)
