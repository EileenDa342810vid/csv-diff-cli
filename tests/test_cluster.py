"""Tests for csv_diff.cluster."""
from __future__ import annotations

import pytest

from csv_diff.cluster import (
    ClusterError,
    EventCluster,
    cluster_diff,
    format_clusters,
    parse_cluster_gap,
)
from csv_diff.diff import RowAdded, RowModified, RowRemoved


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(key: str = "1") -> RowAdded:
    return RowAdded(row={"id": key, "name": "Alice"})


def _removed(key: str = "2") -> RowRemoved:
    return RowRemoved(row={"id": key, "name": "Bob"})


def _modified(key: str = "3") -> RowModified:
    return RowModified(
        key=key,
        old_row={"id": key, "name": "Carol"},
        new_row={"id": key, "name": "Caroline"},
    )


# ---------------------------------------------------------------------------
# parse_cluster_gap
# ---------------------------------------------------------------------------

def test_parse_cluster_gap_none_returns_none():
    assert parse_cluster_gap(None) is None


def test_parse_cluster_gap_integer_passthrough():
    assert parse_cluster_gap(3) == 3


def test_parse_cluster_gap_string_integer():
    assert parse_cluster_gap("5") == 5


def test_parse_cluster_gap_zero_allowed():
    assert parse_cluster_gap(0) == 0


def test_parse_cluster_gap_raises_on_non_integer():
    with pytest.raises(ClusterError):
        parse_cluster_gap("abc")


def test_parse_cluster_gap_raises_on_negative():
    with pytest.raises(ClusterError):
        parse_cluster_gap(-1)


# ---------------------------------------------------------------------------
# cluster_diff
# ---------------------------------------------------------------------------

def test_empty_diff_returns_empty_list():
    assert cluster_diff([], gap=0) == []


def test_single_event_returns_one_cluster():
    result = cluster_diff([_added()], gap=0)
    assert len(result) == 1
    assert result[0].size == 1


def test_gap_zero_splits_each_event():
    events = [_added(), _removed(), _modified()]
    result = cluster_diff(events, gap=0)
    assert len(result) == 3
    for cluster in result:
        assert cluster.size == 1


def test_gap_one_merges_all_consecutive():
    events = [_added(), _removed(), _modified()]
    result = cluster_diff(events, gap=1)
    assert len(result) == 1
    assert result[0].size == 3


def test_cluster_counts_by_type():
    events = [_added("1"), _added("2"), _removed("3"), _modified("4")]
    result = cluster_diff(events, gap=5)
    assert len(result) == 1
    c = result[0]
    assert c.added == 2
    assert c.removed == 1
    assert c.modified == 1


# ---------------------------------------------------------------------------
# format_clusters
# ---------------------------------------------------------------------------

def test_format_clusters_empty():
    assert format_clusters([]) == "No clusters."


def test_format_clusters_contains_header():
    clusters = cluster_diff([_added()], gap=0)
    output = format_clusters(clusters)
    assert "Cluster" in output
    assert "Added" in output


def test_format_clusters_row_count():
    events = [_added(), _removed()]
    clusters = cluster_diff(events, gap=0)
    output = format_clusters(clusters)
    # Two clusters → header + 2 data rows
    lines = [l for l in output.splitlines() if l.strip()]
    assert len(lines) == 3
