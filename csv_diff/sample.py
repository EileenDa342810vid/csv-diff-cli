"""Sampling support: limit diff output to a random or head sample."""

from __future__ import annotations

import random
from typing import List, Optional, Union

from csv_diff.diff import RowAdded, RowModified, RowRemoved

DiffEvent = Union[RowAdded, RowRemoved, RowModified]


class SampleError(ValueError):
    """Raised when sample arguments are invalid."""


def parse_sample_size(value: object) -> Optional[int]:
    """Return an int sample size or None if value is None."""
    if value is None:
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise SampleError(f"Sample size must be an integer, got: {value!r}")
    if n <= 0:
        raise SampleError(f"Sample size must be positive, got: {n}")
    return n


def sample_diff(
    events: List[DiffEvent],
    n: Optional[int],
    *,
    mode: str = "head",
    seed: Optional[int] = None,
) -> List[DiffEvent]:
    """Return at most *n* events from *events*.

    Parameters
    ----------
    mode:
        ``"head"`` – take the first *n* events (default).
        ``"random"`` – draw *n* events at random without replacement.
    seed:
        Optional RNG seed used when ``mode="random"``.
    """
    if n is None:
        return events
    if mode not in {"head", "random"}:
        raise SampleError(f"Unknown sample mode: {mode!r}. Choose 'head' or 'random'.")
    if mode == "head":
        return events[:n]
    rng = random.Random(seed)
    k = min(n, len(events))
    return rng.sample(events, k)
