"""Similarity scoring between two CSV diffs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class ScoreError(Exception):
    pass


@dataclass
class SimilarityScore:
    total_rows: int
    changed_rows: int
    score: float  # 0.0 (all changed) .. 1.0 (identical)
    grade: str


def _grade(score: float) -> str:
    if score >= 0.95:
        return "A"
    if score >= 0.80:
        return "B"
    if score >= 0.60:
        return "C"
    if score >= 0.40:
        return "D"
    return "F"


def compute_score(diff: list, total_rows: int) -> SimilarityScore:
    """Compute a similarity score from a diff result."""
    if total_rows < 0:
        raise ScoreError("total_rows must be non-negative")
    changed = sum(
        1 for e in diff if isinstance(e, (RowAdded, RowRemoved, RowModified))
    )
    if total_rows == 0:
        score = 1.0
    else:
        score = max(0.0, 1.0 - changed / total_rows)
    return SimilarityScore(
        total_rows=total_rows,
        changed_rows=changed,
        score=round(score, 4),
        grade=_grade(score),
    )


def format_score(s: SimilarityScore) -> str:
    lines = [
        "=== Similarity Score ===",
        f"  Total rows  : {s.total_rows}",
        f"  Changed rows: {s.changed_rows}",
        f"  Score       : {s.score:.2%}",
        f"  Grade       : {s.grade}",
    ]
    return "\n".join(lines)
