"""Threshold filtering: suppress exit-nonzero or output unless change count exceeds a limit."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from csv_diff.stats import DiffStats


class ThresholdError(ValueError):
    pass


@dataclass
class ThresholdConfig:
    min_changes: int


def parse_threshold(value: Optional[str | int]) -> Optional[ThresholdConfig]:
    if value is None:
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ThresholdError(f"Threshold must be an integer, got {value!r}")
    if n < 1:
        raise ThresholdError(f"Threshold must be >= 1, got {n}")
    return ThresholdConfig(min_changes=n)


def exceeds_threshold(stats: DiffStats, config: Optional[ThresholdConfig]) -> bool:
    """Return True when changes meet or exceed the threshold (or no threshold set)."""
    if config is None:
        return True
    total = stats.added + stats.removed + stats.modified
    return total >= config.min_changes


def describe_threshold(config: ThresholdConfig, stats: DiffStats) -> str:
    total = stats.added + stats.removed + stats.modified
    return (
        f"Changes ({total}) did not meet threshold ({config.min_changes}); "
        "output suppressed."
    )
