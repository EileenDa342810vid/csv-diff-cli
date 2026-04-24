"""Tests for csv_diff.audit."""
from __future__ import annotations

import pytest

from csv_diff.audit import (
    AuditRecord,
    audit_diff,
    format_audit,
    generate_run_id,
    _event_type,
    _event_detail,
)
from csv_diff.diff import RowAdded, RowRemoved, RowModified


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(row: dict) -> RowAdded:
    return RowAdded(row=row)


def _removed(row: dict) -> RowRemoved:
    return RowRemoved(row=row)


def _modified(old: dict, new: dict) -> RowModified:
    changes = {k: (old[k], new[k]) for k in old if old[k] != new.get(k)}
    return RowModified(old_row=old, new_row=new, changes=changes)


# ---------------------------------------------------------------------------
# generate_run_id
# ---------------------------------------------------------------------------

def test_generate_run_id_returns_string():
    rid = generate_run_id()
    assert isinstance(rid, str) and len(rid) > 0


def test_generate_run_id_unique():
    assert generate_run_id() != generate_run_id()


# ---------------------------------------------------------------------------
# _event_type
# ---------------------------------------------------------------------------

def test_event_type_added():
    assert _event_type(_added({"id": "1"})) == "added"


def test_event_type_removed():
    assert _event_type(_removed({"id": "1"})) == "removed"


def test_event_type_modified():
    assert _event_type(_modified({"id": "1", "v": "a"}, {"id": "1", "v": "b"})) == "modified"


# ---------------------------------------------------------------------------
# audit_diff
# ---------------------------------------------------------------------------

def test_empty_diff_returns_empty_list():
    records = audit_diff([], key_column="id")
    assert records == []


def test_audit_diff_added_row():
    events = [_added({"id": "42", "name": "Alice"})]
    records = audit_diff(events, key_column="id", run_id="RUN1", timestamp="2024-01-01T00:00:00Z")
    assert len(records) == 1
    r = records[0]
    assert isinstance(r, AuditRecord)
    assert r.run_id == "RUN1"
    assert r.timestamp == "2024-01-01T00:00:00Z"
    assert r.event_type == "added"
    assert r.key == "42"


def test_audit_diff_removed_row():
    events = [_removed({"id": "7", "name": "Bob"})]
    records = audit_diff(events, key_column="id", run_id="R", timestamp="T")
    assert records[0].event_type == "removed"
    assert records[0].key == "7"


def test_audit_diff_modified_row_lists_changed_columns():
    events = [_modified({"id": "3", "score": "10"}, {"id": "3", "score": "20"})]
    records = audit_diff(events, key_column="id", run_id="R", timestamp="T")
    assert "score" in records[0].detail


def test_audit_diff_auto_generates_run_id():
    events = [_added({"id": "1"})]
    records = audit_diff(events, key_column="id")
    assert records[0].run_id  # non-empty


def test_all_records_share_same_run_id():
    events = [_added({"id": "1"}), _removed({"id": "2"})]
    records = audit_diff(events, key_column="id", run_id="SHARED")
    assert all(r.run_id == "SHARED" for r in records)


# ---------------------------------------------------------------------------
# format_audit
# ---------------------------------------------------------------------------

def test_format_audit_empty_returns_no_changes_message():
    out = format_audit([])
    assert "no changes" in out.lower()


def test_format_audit_contains_run_id():
    events = [_added({"id": "1"})]
    records = audit_diff(events, key_column="id", run_id="XYZ", timestamp="T")
    out = format_audit(records)
    assert "XYZ" in out


def test_format_audit_contains_event_type():
    events = [_added({"id": "5"})]
    records = audit_diff(events, key_column="id", run_id="R", timestamp="T")
    out = format_audit(records)
    assert "added" in out
