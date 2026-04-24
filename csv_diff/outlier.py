"""Detect statistical outliers in numeric columns across diff events."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class OutlierError(Exception):
    """Raised when outlier detection configuration is invalid."""


@dataclass
class OutlierResult:
    column: str
    mean: float
    std: float
    threshold: float
    outliers: List[Dict[str, str]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.outliers)


def parse_outlier_columns(value: Optional[str]) -> Optional[List[str]]:
    """Parse a comma-separated list of column names, or return None."""
    if not value or not value.strip():
        return None
    parts = [p.strip() for p in value.split(",")]
    if any(p == "" for p in parts):
        raise OutlierError("Column list contains an empty entry.")
    return parts


def parse_z_threshold(value: Optional[float]) -> float:
    """Return the z-score threshold, defaulting to 3.0."""
    if value is None:
        return 3.0
    try:
        threshold = float(value)
    except (TypeError, ValueError):
        raise OutlierError(f"Z-score threshold must be a number, got: {value!r}")
    if threshold <= 0:
        raise OutlierError("Z-score threshold must be positive.")
    return threshold


def _extract_values(
    events: Sequence, column: str
) -> List[Dict[str, str]]:
    """Collect all changed rows that have a value for *column*."""
    rows: List[Dict[str, str]] = []
    for event in events:
        if isinstance(event, (RowAdded, RowRemoved)):
            row = event.row
            if column in row:
                rows.append(row)
        elif isinstance(event, RowModified):
            for row in (event.old_row, event.new_row):
                if column in row:
                    rows.append(row)
    return rows


def detect_outliers(
    events: Sequence,
    columns: List[str],
    z_threshold: float = 3.0,
) -> Dict[str, OutlierResult]:
    """Return a mapping of column -> OutlierResult for each requested column."""
    results: Dict[str, OutlierResult] = {}
    for col in columns:
        rows = _extract_values(events, col)
        numeric: List[float] = []
        for row in rows:
            try:
                numeric.append(float(row[col]))
            except (ValueError, TypeError):
                pass
        if len(numeric) < 2:
            results[col] = OutlierResult(col, 0.0, 0.0, z_threshold, [])
            continue
        mean = sum(numeric) / len(numeric)
        variance = sum((x - mean) ** 2 for x in numeric) / len(numeric)
        std = variance ** 0.5
        outlier_rows: List[Dict[str, str]] = []
        if std > 0:
            for row in rows:
                try:
                    z = abs(float(row[col]) - mean) / std
                except (ValueError, TypeError):
                    continue
                if z > z_threshold:
                    outlier_rows.append(row)
        results[col] = OutlierResult(col, mean, std, z_threshold, outlier_rows)
    return results


def format_outliers(results: Dict[str, OutlierResult]) -> Optional[str]:
    """Return a human-readable summary of outlier results, or None if empty."""
    if not results:
        return None
    lines: List[str] = ["=== Outlier Detection ==="]
    for col, result in results.items():
        lines.append(
            f"  {col}: mean={result.mean:.4g}, std={result.std:.4g}, "
            f"threshold=\u00b1{result.threshold}\u03c3"
        )
        if result.outliers:
            lines.append(f"    {result.count} outlier(s) detected:")
            for row in result.outliers:
                lines.append(f"      {row}")
        else:
            lines.append("    No outliers detected.")
    return "\n".join(lines)
