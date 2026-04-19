"""Split diff output into per-type buckets (added/removed/modified)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from csv_diff.diff import RowAdded, RowRemoved, RowModified


class SplitError(Exception):
    pass


@dataclass
class SplitResult:
    added: List[RowAdded] = field(default_factory=list)
    removed: List[RowRemoved] = field(default_factory=list)
    modified: List[RowModified] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)


def split_diff(events: list) -> SplitResult:
    """Partition diff events into a SplitResult by event type."""
    result = SplitResult()
    for event in events:
        if isinstance(event, RowAdded):
            result.added.append(event)
        elif isinstance(event, RowRemoved):
            result.removed.append(event)
        elif isinstance(event, RowModified):
            result.modified.append(event)
        else:
            raise SplitError(f"Unknown event type: {type(event)}")
    return result


def format_split(result: SplitResult) -> str:
    """Return a human-readable summary of the split result."""
    lines = ["=== Split Summary ==="]
    lines.append(f"  Added   : {len(result.added)}")
    lines.append(f"  Removed : {len(result.removed)}")
    lines.append(f"  Modified: {len(result.modified)}")
    lines.append(f"  Total   : {result.total}")
    return "\n".join(lines)
