"""Group diff events by a column value."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from csv_diff.diff import RowAdded, RowRemoved, RowModified

DiffEvent = RowAdded | RowRemoved | RowModified


class GroupError(Exception):
    pass


@dataclass
class ColumnGroup:
    column: str
    added: List[DiffEvent] = field(default_factory=list)
    removed: List[DiffEvent] = field(default_factory=list)
    modified: List[DiffEvent] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)


def parse_group_by(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def validate_group_column(column: str, headers: List[str]) -> None:
    if column not in headers:
        raise GroupError(f"Group-by column '{column}' not found in headers: {headers}")


def group_diff(events: List[DiffEvent], column: str) -> Dict[str, ColumnGroup]:
    groups: Dict[str, ColumnGroup] = {}

    for event in events:
        if isinstance(event, RowAdded):
            val = event.row.get(column, "")
            row_data = event.row
        elif isinstance(event, RowRemoved):
            val = event.row.get(column, "")
            row_data = event.row
        elif isinstance(event, RowModified):
            val = event.before.get(column, "")
            row_data = event.before
        else:
            continue

        if val not in groups:
            groups[val] = ColumnGroup(column=column)

        if isinstance(event, RowAdded):
            groups[val].added.append(event)
        elif isinstance(event, RowRemoved):
            groups[val].removed.append(event)
        elif isinstance(event, RowModified):
            groups[val].modified.append(event)

    return groups


def format_groups(groups: Dict[str, ColumnGroup], column: str) -> str:
    if not groups:
        return "No changes to group."
    lines = [f"Grouped by '{column}':\n"]
    for val, grp in sorted(groups.items()):
        lines.append(f"  {column}={val!r}  added={len(grp.added)}  removed={len(grp.removed)}  modified={len(grp.modified)}")
    return "\n".join(lines)
