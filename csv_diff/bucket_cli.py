"""CLI helpers for the --bucket-by feature."""
from __future__ import annotations

import sys
from typing import Optional, Sequence

from csv_diff.bucket import (
    BucketError,
    bucket_diff,
    format_bucket_table,
    parse_bucket_column,
    parse_bucket_edges,
)


def add_bucket_arguments(parser) -> None:
    parser.add_argument(
        "--bucket-by",
        metavar="COLUMN",
        default=None,
        help="Column to bucket diff events by (requires --bucket-edges).",
    )
    parser.add_argument(
        "--bucket-edges",
        metavar="EDGES",
        default=None,
        help="Comma-separated ascending numeric edges, e.g. '0,100,500'.",
    )


def maybe_print_buckets(args, events: Sequence) -> bool:
    """Return True if bucket output was requested and printed."""
    column = parse_bucket_column(getattr(args, "bucket_by", None))
    if column is None:
        return False
    edges_raw = getattr(args, "bucket_edges", None)
    if not edges_raw:
        print(
            "error: --bucket-by requires --bucket-edges",
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        edges = parse_bucket_edges(edges_raw)
        buckets = bucket_diff(events, column, edges)
    except BucketError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    print(format_bucket_table(buckets))
    return True
