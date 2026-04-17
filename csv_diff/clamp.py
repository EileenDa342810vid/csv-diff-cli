"""Clamp numeric column values to a specified range for diff comparison."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


class ClampError(Exception):
    pass


@dataclass
class ClampRule:
    column: str
    min_val: Optional[float]
    max_val: Optional[float]


def parse_clamp_rules(spec: Optional[str]) -> Optional[List[ClampRule]]:
    """Parse clamp spec like 'age:0:120,score:0:100'."""
    if not spec or not spec.strip():
        return None
    rules: List[ClampRule] = []
    for entry in spec.split(","):
        entry = entry.strip()
        if not entry:
            raise ClampError(f"Empty clamp entry in spec: {spec!r}")
        parts = entry.split(":")
        if len(parts) != 3:
            raise ClampError(
                f"Clamp entry {entry!r} must be 'column:min:max' (use '' for no bound)"
            )
        col, raw_min, raw_max = parts
        col = col.strip()
        if not col:
            raise ClampError("Column name must not be empty in clamp spec")
        try:
            min_val = float(raw_min) if raw_min.strip() else None
            max_val = float(raw_max) if raw_max.strip() else None
        except ValueError as exc:
            raise ClampError(f"Non-numeric bound in clamp entry {entry!r}: {exc}") from exc
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ClampError(
                f"min ({min_val}) exceeds max ({max_val}) for column {col!r}"
            )
        rules.append(ClampRule(column=col, min_val=min_val, max_val=max_val))
    return rules


def validate_clamp_rules(rules: List[ClampRule], headers: List[str]) -> None:
    missing = [r.column for r in rules if r.column not in headers]
    if missing:
        raise ClampError(f"Clamp columns not found in headers: {missing}")


def _clamp_value(value: str, rule: ClampRule) -> str:
    try:
        num = float(value)
    except ValueError:
        return value
    if rule.min_val is not None:
        num = max(rule.min_val, num)
    if rule.max_val is not None:
        num = min(rule.max_val, num)
    return str(int(num)) if num == int(num) else str(num)


def apply_clamps(row: Dict[str, str], rules: List[ClampRule]) -> Dict[str, str]:
    result = dict(row)
    for rule in rules:
        if rule.column in result:
            result[rule.column] = _clamp_value(result[rule.column], rule)
    return result


def clamp_rows(
    rows: List[Dict[str, str]], rules: Optional[List[ClampRule]]
) -> List[Dict[str, str]]:
    if not rules:
        return rows
    return [apply_clamps(row, rules) for row in rows]
