"""CLI helpers for the --tag feature."""

from __future__ import annotations

from typing import List, Optional

from csv_diff.tag import TagError, TaggedEvent, format_tags, parse_tag_rules, tag_diff


def add_tag_arguments(parser) -> None:
    parser.add_argument(
        "--tag",
        metavar="RULES",
        default=None,
        help=(
            "Tag diff rows using comma-separated rules of the form "
            "'label:column:pattern'. Example: urgent:status:FAIL"
        ),
    )


def resolve_tags(args, events: list) -> List[TaggedEvent]:
    """Parse --tag spec and apply to events; exits with code 2 on bad spec."""
    import sys

    rules = None
    if getattr(args, "tag", None):
        try:
            rules = parse_tag_rules(args.tag)
        except TagError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(2)
    return tag_diff(events, rules)


def maybe_print_tags(tagged: List[TaggedEvent], formatter) -> None:
    """Inject tag labels into formatted output lines."""
    for te in tagged:
        label = format_tags(te)
        line = formatter(te.event)
        if label:
            print(f"{label} {line}")
        else:
            print(line)
