"""Classify diff severity based on change counts and thresholds."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csv_diff.stats import DiffStats


class SeverityError(ValueError):
    pass


SEVERITY_LEVELS = ("none", "low", "medium", "high")


@dataclass(frozen=True)
class SeverityConfig:
    low: int = 1
    medium: int = 10
    high: int = 50


def parse_severity_config(
    low: Optional[int] = None,
    medium: Optional[int] = None,
    high: Optional[int] = None,
) -> SeverityConfig:
    cfg = SeverityConfig(
        low=low if low is not None else 1,
        medium=medium if medium is not None else 10,
        high=high if high is not None else 50,
    )
    if not (0 < cfg.low <= cfg.medium <= cfg.high):
        raise SeverityError(
            f"Severity thresholds must satisfy 0 < low <= medium <= high, got "
            f"low={cfg.low}, medium={cfg.medium}, high={cfg.high}"
        )
    return cfg


def classify(stats: DiffStats, cfg: Optional[SeverityConfig] = None) -> str:
    """Return a severity label for the given diff stats."""
    if cfg is None:
        cfg = SeverityConfig()
    total = stats.added + stats.removed + stats.modified
    if total == 0:
        return "none"
    if total < cfg.medium:
        return "low"
    if total < cfg.high:
        return "medium"
    return "high"


def format_severity(level: str) -> str:
    labels = {
        "none": "No changes detected.",
        "low": "Low severity: few changes detected.",
        "medium": "Medium severity: moderate number of changes detected.",
        "high": "High severity: large number of changes detected.",
    }
    return labels.get(level, f"Unknown severity level: {level}")
