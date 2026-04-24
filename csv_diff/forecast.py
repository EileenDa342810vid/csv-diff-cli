"""forecast.py – simple linear-trend forecasting over numeric diff columns.

Given a sequence of diff events and a target column, extracts the numeric
values that *changed*, fits a least-squares linear trend, and projects the
next N values forward.

Public API
----------
parse_forecast_column  – validate / normalise the column name argument
parse_forecast_steps   – validate the number of steps to project
compute_forecast       – run the trend fit and return a ForecastResult
format_forecast        – render a ForecastResult as a human-readable string
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from csv_diff.diff import RowAdded, RowModified, RowRemoved

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ForecastError(Exception):
    """Raised when forecasting cannot be performed."""


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------


def parse_forecast_column(value: Optional[str]) -> Optional[str]:
    """Return the stripped column name, or *None* if *value* is empty."""
    if not value or not value.strip():
        return None
    return value.strip()


def parse_forecast_steps(value) -> int:
    """Coerce *value* to a positive integer number of forecast steps.

    Accepts an existing ``int`` or a string representation.
    Raises :class:`ForecastError` for invalid input.
    """
    if value is None:
        return 3  # sensible default
    try:
        steps = int(value)
    except (TypeError, ValueError):
        raise ForecastError(f"forecast steps must be an integer, got {value!r}")
    if steps < 1:
        raise ForecastError("forecast steps must be >= 1")
    return steps


# ---------------------------------------------------------------------------
# Core data structures
# ---------------------------------------------------------------------------


@dataclass
class ForecastResult:
    """Holds the outcome of a linear forecast."""

    column: str
    observed: List[float] = field(default_factory=list)
    slope: float = 0.0
    intercept: float = 0.0
    projected: List[float] = field(default_factory=list)

    @property
    def n_observed(self) -> int:
        return len(self.observed)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_values(
    events: Sequence, column: str
) -> List[float]:
    """Pull numeric values for *column* from changed rows in *events*.

    For :class:`RowModified` events the *new* value is used.  Added and
    removed rows also contribute their single value so that the trend
    reflects the full history of changes.
    """
    values: List[float] = []
    for ev in events:
        row: Optional[dict] = None
        if isinstance(ev, RowModified):
            row = ev.new_row
        elif isinstance(ev, RowAdded):
            row = ev.row
        elif isinstance(ev, RowRemoved):
            row = ev.row
        if row is None or column not in row:
            continue
        raw = row[column]
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            pass  # skip non-numeric cells silently
    return values


def _linear_fit(values: List[float]):
    """Return *(slope, intercept)* via ordinary least squares."""
    n = len(values)
    if n < 2:
        return 0.0, values[0] if values else 0.0
    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den else 0.0
    intercept = y_mean - slope * x_mean
    return slope, intercept


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compute_forecast(
    events: Sequence,
    column: str,
    steps: int = 3,
) -> ForecastResult:
    """Fit a linear trend to changed values in *column* and project *steps* ahead.

    Raises :class:`ForecastError` when there are fewer than two observed
    data points (a trend cannot be determined from a single value).
    """
    observed = _extract_values(events, column)
    if len(observed) < 2:
        raise ForecastError(
            f"need at least 2 numeric observations in column {column!r} to forecast "
            f"(found {len(observed)})"
        )
    slope, intercept = _linear_fit(observed)
    n = len(observed)
    projected = [intercept + slope * (n + i) for i in range(steps)]
    return ForecastResult(
        column=column,
        observed=observed,
        slope=slope,
        intercept=intercept,
        projected=projected,
    )


def format_forecast(result: ForecastResult) -> str:
    """Render a :class:`ForecastResult` as a compact, human-readable block."""
    lines = [
        f"Forecast  column : {result.column}",
        f"          trend  : {result.slope:+.4f} per step",
        f"          observed ({result.n_observed}): "
        + ", ".join(f"{v:.2f}" for v in result.observed),
        "          projected: "
        + ", ".join(f"{v:.2f}" for v in result.projected),
    ]
    return "\n".join(lines)
