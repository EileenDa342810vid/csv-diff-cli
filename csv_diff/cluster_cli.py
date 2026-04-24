"""CLI helpers for the --cluster-gap feature."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Sequence

from csv_diff.cluster import ClusterError, EventCluster, cluster_diff, format_clusters, parse_cluster_gap

DiffEvent = object  # avoid circular import at type-check time


def add_cluster_arguments(parser: argparse.ArgumentParser) -> None:
    """Register --cluster-gap on *parser*."""
    parser.add_argument(
        "--cluster-gap",
        metavar="N",
        default=None,
        help=(
            "Group consecutive changed rows into clusters. "
            "N=0 keeps each change in its own cluster; "
            "N>=1 merges all consecutive changes into one cluster."
        ),
    )


def maybe_print_clusters(
    args: argparse.Namespace,
    events: Sequence,
) -> bool:
    """Print cluster summary if --cluster-gap was requested.

    Returns *True* when output was produced so the caller can decide
    whether to suppress the normal diff output.
    """
    raw = getattr(args, "cluster_gap", None)
    if raw is None:
        return False

    try:
        gap = parse_cluster_gap(raw)
    except ClusterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    clusters = cluster_diff(list(events), gap=gap)  # type: ignore[arg-type]
    print(format_clusters(clusters))
    return True
