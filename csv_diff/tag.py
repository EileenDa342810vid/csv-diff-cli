"""Tag diff events with user-defined labels based on column value patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csv_diff.diff import RowAdded, RowModified, RowRemoved


class TagError(Exception):
    pass


@dataclass
class TagRule:
    label: str
    column: str
    pattern: re.Pattern


@dataclass
class TaggedEvent:
    event: object
    tags: List[str] = field(default_factory=list)


def parse_tag_rules(spec: Optional[str]) -> Optional[List[TagRule]]:
    """Parse rules from 'label:column:pattern,...' string."""
    if not spec or not spec.strip():
        return None
    rules: List[TagRule] = []
    for part in spec.split(","):
        part = part.strip()
        segments = part.split(":", 2)
        if len(segments) != 3:
            raise TagError(f"Invalid tag rule {part!r}: expected 'label:column:pattern'")
        label, column, pattern = (s.strip() for s in segments)
        if not label or not column or not pattern:
            raise TagError(f"Empty segment in tag rule {part!r}")
        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            raise TagError(f"Bad regex {pattern!r}: {exc}") from exc
        rules.append(TagRule(label=label, column=column, pattern=compiled))
    return rules


def _row_values(event) -> Dict[str, str]:
    if isinstance(event, RowAdded):
        return event.row
    if isinstance(event, RowRemoved):
        return event.row
    if isinstance(event, RowModified):
        return event.new_row
    return {}


def tag_event(event, rules: List[TagRule]) -> TaggedEvent:
    values = _row_values(event)
    tags = [
        r.label
        for r in rules
        if r.column in values and r.pattern.search(values[r.column])
    ]
    return TaggedEvent(event=event, tags=tags)


def tag_diff(events: list, rules: Optional[List[TagRule]]) -> List[TaggedEvent]:
    if not rules:
        return [TaggedEvent(event=e) for e in events]
    return [tag_event(e, rules) for e in events]


def format_tags(tagged: TaggedEvent) -> str:
    if not tagged.tags:
        return ""
    return "[" + ", ".join(tagged.tags) + "]"
