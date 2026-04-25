"""Hedge: flag diff events whose changed values cross a numeric boundary.

A hedge rule specifies a column and a threshold value.  Any RowModified
event where the old *or* new value crosses from below to above (or above
to below) that threshold is marked as a hedge hit.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from .diff import RowModified


class HedgeError(Exception):
    pass


@dataclass
class HedgeRule:
    column: str
    threshold: float


@dataclass
class HedgeHit:
    key: str
    column: str
    old_value: str
    new_value: str
    threshold: float


def parse_hedge_rules(spec: Optional[str]) -> Optional[List[HedgeRule]]:
    """Parse 'col:threshold,...' into HedgeRule list, or return None."""
    if not spec or not spec.strip():
        return None
    rules: List[HedgeRule] = []
    for part in spec.split(","):
        part = part.strip()
        if ":" not in part:
            raise HedgeError(
                f"Invalid hedge rule {part!r}: expected 'column:threshold'"
            )
        col, raw = part.split(":", 1)
        col = col.strip()
        raw = raw.strip()
        if not col:
            raise HedgeError("Hedge rule has empty column name")
        try:
            threshold = float(raw)
        except ValueError:
            raise HedgeError(
                f"Hedge threshold {raw!r} for column {col!r} is not numeric"
            )
        rules.append(HedgeRule(column=col, threshold=threshold))
    return rules or None


def validate_hedge_columns(
    rules: List[HedgeRule], headers: Sequence[str]
) -> None:
    header_set = set(headers)
    for rule in rules:
        if rule.column not in header_set:
            raise HedgeError(
                f"Hedge column {rule.column!r} not found in headers"
            )


def _crosses(old: str, new: str, threshold: float) -> bool:
    """Return True when old and new are on opposite sides of threshold."""
    try:
        old_f = float(old)
        new_f = float(new)
    except (ValueError, TypeError):
        return False
    return (old_f < threshold) != (new_f < threshold)


def find_hedge_hits(
    events: Sequence, rules: List[HedgeRule]
) -> List[HedgeHit]:
    hits: List[HedgeHit] = []
    for event in events:
        if not isinstance(event, RowModified):
            continue
        for rule in rules:
            old_val = event.old_row.get(rule.column, "")
            new_val = event.new_row.get(rule.column, "")
            if _crosses(old_val, new_val, rule.threshold):
                hits.append(
                    HedgeHit(
                        key=str(event.key),
                        column=rule.column,
                        old_value=old_val,
                        new_value=new_val,
                        threshold=rule.threshold,
                    )
                )
    return hits


def format_hedge_hits(hits: List[HedgeHit]) -> str:
    if not hits:
        return "Hedge: no threshold crossings detected."
    lines = ["Hedge threshold crossings:"]
    for h in hits:
        lines.append(
            f"  key={h.key}  column={h.column}  "
            f"{h.old_value} -> {h.new_value}  (threshold {h.threshold})"
        )
    return "\n".join(lines)
