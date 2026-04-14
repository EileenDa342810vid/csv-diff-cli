"""Core diffing logic for comparing two CSV datasets."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RowAdded:
    key: str
    row: dict[str, Any]


@dataclass
class RowRemoved:
    key: str
    row: dict[str, Any]


@dataclass
class RowModified:
    key: str
    old_row: dict[str, Any]
    new_row: dict[str, Any]
    changed_columns: list[str] = field(default_factory=list)


DiffResult = list[RowAdded | RowRemoved | RowModified]


def diff_csv(
    old_rows: list[dict[str, Any]],
    new_rows: list[dict[str, Any]],
    key_column: str,
) -> DiffResult:
    """Compare two lists of CSV row dicts and return a list of diff events.

    Args:
        old_rows: Rows from the original CSV file.
        new_rows: Rows from the updated CSV file.
        key_column: Column name used as the unique row identifier.

    Returns:
        A list of RowAdded, RowRemoved, or RowModified instances.
    """
    old_map: dict[str, dict[str, Any]] = {row[key_column]: row for row in old_rows}
    new_map: dict[str, dict[str, Any]] = {row[key_column]: row for row in new_rows}

    results: DiffResult = []

    for key, old_row in old_map.items():
        if key not in new_map:
            results.append(RowRemoved(key=key, row=old_row))
        else:
            new_row = new_map[key]
            changed = [
                col
                for col in old_row
                if col in new_row and old_row[col] != new_row[col]
            ]
            if changed:
                results.append(
                    RowModified(
                        key=key,
                        old_row=old_row,
                        new_row=new_row,
                        changed_columns=changed,
                    )
                )

    for key, new_row in new_map.items():
        if key not in old_map:
            results.append(RowAdded(key=key, row=new_row))

    return results
