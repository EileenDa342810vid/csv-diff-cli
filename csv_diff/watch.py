"""File-watching support: poll two CSV paths and re-run a diff callback."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional


class WatchError(Exception):
    """Raised when watch configuration is invalid."""


@dataclass
class WatchState:
    """Tracks last-seen modification times for the two watched files."""

    path_a: Path
    path_b: Path
    _mtimes: List[float] = field(default_factory=lambda: [-1.0, -1.0])

    def changed(self) -> bool:
        """Return True if either file has been modified since last check."""
        new = [self.path_a.stat().st_mtime, self.path_b.stat().st_mtime]
        if new != self._mtimes:
            self._mtimes = new
            return True
        return False


def parse_interval(value: Optional[object]) -> float:
    """Parse and validate a polling interval (seconds)."""
    if value is None:
        return 2.0
    try:
        interval = float(value)
    except (TypeError, ValueError):
        raise WatchError(f"Interval must be a number, got {value!r}")
    if interval <= 0:
        raise WatchError(f"Interval must be positive, got {interval}")
    return interval


def watch(
    path_a: Path,
    path_b: Path,
    callback: Callable[[], None],
    interval: float = 2.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll *path_a* and *path_b* every *interval* seconds.

    Calls *callback* whenever a change is detected.  Runs until interrupted
    (KeyboardInterrupt) or *max_iterations* polls have been performed (useful
    for testing).
    """
    if not path_a.exists():
        raise WatchError(f"File not found: {path_a}")
    if not path_b.exists():
        raise WatchError(f"File not found: {path_b}")

    state = WatchState(path_a=path_a, path_b=path_b)
    # Prime the state so the very first poll does not always fire.
    state.changed()

    iterations = 0
    try:
        while True:
            if state.changed():
                callback()
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
