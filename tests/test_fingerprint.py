"""Tests for csv_diff.fingerprint."""

from __future__ import annotations

import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.fingerprint import (
    DiffFingerprint,
    FingerprintError,
    compute_fingerprint,
    format_fingerprint,
)


def _added(row: dict) -> RowAdded:
    return RowAdded(row=row)


def _removed(row: dict) -> RowRemoved:
    return RowRemoved(row=row)


def _modified(old: dict, new: dict) -> RowModified:
    return RowModified(old_row=old, new_row=new)


def test_empty_diff_returns_fingerprint():
    fp = compute_fingerprint([])
    assert isinstance(fp, DiffFingerprint)
    assert len(fp.hex) == 64  # sha256 hex digest
    assert fp.event_count == 0


def test_identical_diffs_produce_same_fingerprint():
    events = [_added({"id": "1", "name": "Alice"})]
    fp1 = compute_fingerprint(events)
    fp2 = compute_fingerprint(events)
    assert fp1.hex == fp2.hex


def test_different_diffs_produce_different_fingerprints():
    fp1 = compute_fingerprint([_added({"id": "1", "name": "Alice"})])
    fp2 = compute_fingerprint([_added({"id": "2", "name": "Bob"})])
    assert fp1.hex != fp2.hex


def test_event_count_matches_input():
    events = [
        _added({"id": "1"}),
        _removed({"id": "2"}),
        _modified({"id": "3", "v": "a"}, {"id": "3", "v": "b"}),
    ]
    fp = compute_fingerprint(events)
    assert fp.event_count == 3


def test_short_returns_prefix():
    fp = compute_fingerprint([_added({"id": "1"})])
    assert fp.short() == fp.hex[:8]
    assert fp.short(4) == fp.hex[:4]


def test_order_matters_for_fingerprint():
    a = _added({"id": "1"})
    b = _removed({"id": "2"})
    fp1 = compute_fingerprint([a, b])
    fp2 = compute_fingerprint([b, a])
    assert fp1.hex != fp2.hex


def test_unsupported_algorithm_raises():
    with pytest.raises(FingerprintError, match="Unsupported hash algorithm"):
        compute_fingerprint([], algorithm="notahash")


def test_unknown_event_type_raises():
    with pytest.raises(FingerprintError, match="Unknown event type"):
        compute_fingerprint([object()])  # type: ignore[list-item]


def test_alternative_algorithm_md5():
    fp = compute_fingerprint([_added({"id": "1"})], algorithm="md5")
    assert len(fp.hex) == 32  # md5 hex digest


def test_format_fingerprint_none():
    result = format_fingerprint(None)
    assert result == "Fingerprint: n/a"


def test_format_fingerprint_shows_hex_and_count():
    fp = compute_fingerprint([_added({"id": "1"})])
    result = format_fingerprint(fp)
    assert fp.hex in result
    assert fp.short() in result
    assert "1" in result
