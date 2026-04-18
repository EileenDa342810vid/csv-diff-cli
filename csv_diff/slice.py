"""Row slicing: limit diff output to a range of rows by index."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved

DiffEvent = RowAdded | RowRemoved | RowModified


class SliceError(ValueError):
    """Raised when slice parameters are invalid."""


@dataclass(frozen=True)
class SliceConfig:
    start: int  # inclusive, 0-based
    stop: Optional[int]  # exclusive; None means unbounded


def parse_slice(value: Optional[str]) -> Optional[SliceConfig]:
    """Parse a slice spec like '10' or '5:20' into a SliceConfig."""
    if not value:
        return None
    value = value.strip()
    if ":" in value:
        raw_start, raw_stop = value.split(":", 1)
        start = int(raw_start) if raw_start.strip() else 0
        stop = int(raw_stop) if raw_stop.strip() else None
    else:
        start = 0
        stop = int(value)
    if start < 0:
        raise SliceError("slice start must be >= 0")
    if stop is not None and stop <= start:
        raise SliceError("slice stop must be greater than start")
    return SliceConfig(start=start, stop=stop)


def slice_diff(
    events: Sequence[DiffEvent],
    cfg: Optional[SliceConfig],
) -> List[DiffEvent]:
    """Return only the events within the slice window."""
    if cfg is None:
        return list(events)
    sliced = events[cfg.start : cfg.stop]
    return list(sliced)


def describe_slice(cfg: SliceConfig, total: int) -> str:
    stop_label = cfg.stop if cfg.stop is not None else total
    return f"Showing rows {cfg.start}–{min(stop_label, total)} of {total} change(s)."
