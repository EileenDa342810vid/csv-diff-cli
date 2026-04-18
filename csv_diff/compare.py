"""Column-level value comparison with configurable tolerance for numeric fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class CompareError(Exception):
    pass


@dataclass
class ToleranceConfig:
    column: str
    tolerance: float


def parse_tolerance_specs(raw: Optional[str]) -> Optional[list[ToleranceConfig]]:
    """Parse 'col:0.01,col2:5' into ToleranceConfig list."""
    if not raw or not raw.strip():
        return None
    configs: list[ToleranceConfig] = []
    for part in raw.split(","):
        part = part.strip()
        if ":" not in part:
            raise CompareError(f"Invalid tolerance spec (expected col:value): {part!r}")
        col, _, val = part.partition(":")
        col = col.strip()
        val = val.strip()
        if not col:
            raise CompareError(f"Empty column name in tolerance spec: {part!r}")
        try:
            tol = float(val)
        except ValueError:
            raise CompareError(f"Non-numeric tolerance for column {col!r}: {val!r}")
        if tol < 0:
            raise CompareError(f"Tolerance must be >= 0 for column {col!r}")
        configs.append(ToleranceConfig(column=col, tolerance=tol))
    return configs


def validate_tolerance_columns(configs: list[ToleranceConfig], headers: list[str]) -> None:
    known = set(headers)
    for cfg in configs:
        if cfg.column not in known:
            raise CompareError(f"Tolerance column not found in headers: {cfg.column!r}")


def values_equal(
    col: str,
    a: str,
    b: str,
    tolerance_map: Optional[dict[str, float]] = None,
) -> bool:
    """Return True if a and b should be considered equal for the given column."""
    if a == b:
        return True
    if tolerance_map and col in tolerance_map:
        try:
            return abs(float(a) - float(b)) <= tolerance_map[col]
        except ValueError:
            return False
    return False


def build_tolerance_map(configs: Optional[list[ToleranceConfig]]) -> dict[str, float]:
    if not configs:
        return {}
    return {c.column: c.tolerance for c in configs}
