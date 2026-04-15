"""Core diffing logic for CSV files."""

from dataclasses import dataclass, field
from typing import Optional

from csv_diff.filter import filter_rows, validate_columns


@dataclass
class RowAdded:
    key: str
    row: dict


@dataclass
class RowRemoved:
    key: str
    row: dict


@dataclass
class RowModified:
    key: str
    old_row: dict
    new_row: dict
    changed_fields: list[str] = field(default_factory=list)


DiffResult = list[RowAdded | RowRemoved | RowModified]


def diff_csv(
    old_rows: list[dict],
    new_rows: list[dict],
    key_column: str,
    columns: Optional[list[str]] = None,
) -> DiffResult:
    """Compare two lists of CSV row dicts and return diff events.

    Args:
        old_rows: Rows from the original CSV.
        new_rows: Rows from the new CSV.
        key_column: Column name used as the unique row identifier.
        columns: Optional list of columns to restrict comparison to.

    Returns:
        Ordered list of :class:`RowAdded`, :class:`RowRemoved`, and
        :class:`RowModified` events.
    """
    if columns is not None:
        headers = list(old_rows[0].keys()) if old_rows else list(new_rows[0].keys() if new_rows else [])
        validate_columns(columns, headers)
        old_rows = filter_rows(old_rows, columns if key_column in columns else [key_column] + columns)
        new_rows = filter_rows(new_rows, columns if key_column in columns else [key_column] + columns)

    old_map = {r[key_column]: r for r in old_rows}
    new_map = {r[key_column]: r for r in new_rows}

    results: DiffResult = []

    for key, old_row in old_map.items():
        if key not in new_map:
            results.append(RowRemoved(key=key, row=old_row))
        else:
            new_row = new_map[key]
            changed = [f for f in old_row if old_row.get(f) != new_row.get(f)]
            if changed:
                results.append(
                    RowModified(key=key, old_row=old_row, new_row=new_row, changed_fields=changed)
                )

    for key, new_row in new_map.items():
        if key not in old_map:
            results.append(RowAdded(key=key, row=new_row))

    return results


def summarize_diff(results: DiffResult) -> dict:
    """Return a summary dict with counts of each change type."""
    return {
        "added": sum(1 for r in results if isinstance(r, RowAdded)),
        "removed": sum(1 for r in results if isinstance(r, RowRemoved)),
        "modified": sum(1 for r in results if isinstance(r, RowModified)),
        "unchanged": 0,  # placeholder; requires full row set context
    }
