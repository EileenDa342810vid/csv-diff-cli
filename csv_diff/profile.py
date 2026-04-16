"""Profile a CSV diff result — per-column change rates and value distributions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff.diff import RowAdded, RowRemoved, RowModified


class ProfileError(ValueError):
    pass


@dataclass
class ColumnProfile:
    name: str
    changes: int = 0
    unique_old_values: int = 0
    unique_new_values: int = 0
    top_new_values: List[str] = field(default_factory=list)


@dataclass
class DiffProfile:
    total_rows_a: int = 0
    total_rows_b: int = 0
    columns: Dict[str, ColumnProfile] = field(default_factory=dict)


def _ensure_column(profile: DiffProfile, col: str) -> ColumnProfile:
    if col not in profile.columns:
        profile.columns[col] = ColumnProfile(name=col)
    return profile.columns[col]


def profile_diff(events: list, headers: List[str]) -> DiffProfile:
    """Compute a DiffProfile from a list of diff events."""
    if not isinstance(headers, list):
        raise ProfileError("headers must be a list")

    prof = DiffProfile()
    old_vals: Dict[str, List[str]] = {h: [] for h in headers}
    new_vals: Dict[str, List[str]] = {h: [] for h in headers}

    for event in events:
        if isinstance(event, RowAdded):
            prof.total_rows_b += 1
            for col in headers:
                new_vals[col].append(event.row.get(col, ""))
        elif isinstance(event, RowRemoved):
            prof.total_rows_a += 1
            for col in headers:
                old_vals[col].append(event.row.get(col, ""))
        elif isinstance(event, RowModified):
            prof.total_rows_a += 1
            prof.total_rows_b += 1
            for col in headers:
                ov = event.old_row.get(col, "")
                nv = event.new_row.get(col, "")
                old_vals[col].append(ov)
                new_vals[col].append(nv)
                if ov != nv:
                    _ensure_column(prof, col).changes += 1

    for col in headers:
        cp = _ensure_column(prof, col)
        cp.unique_old_values = len(set(old_vals[col]))
        cp.unique_new_values = len(set(new_vals[col]))
        freq: Dict[str, int] = {}
        for v in new_vals[col]:
            freq[v] = freq.get(v, 0) + 1
        cp.top_new_values = sorted(freq, key=lambda k: -freq[k])[:5]

    return prof


def format_profile(prof: DiffProfile) -> str:
    """Return a human-readable profile summary."""
    lines = [
        f"Rows in A: {prof.total_rows_a}  Rows in B: {prof.total_rows_b}",
        "",
        f"{'Column':<25} {'Changes':>8} {'Uniq-old':>10} {'Uniq-new':>10}",
        "-" * 57,
    ]
    for cp in prof.columns.values():
        lines.append(f"{cp.name:<25} {cp.changes:>8} {cp.unique_old_values:>10} {cp.unique_new_values:>10}")
    return "\n".join(lines)
