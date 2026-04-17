"""Tests for csv_diff.redact."""
import pytest

from csv_diff.diff import RowAdded, RowModified, RowRemoved
from csv_diff.redact import (
    RedactConfig,
    RedactError,
    parse_redact_columns,
    redact_diff,
    redact_event,
    validate_redact_columns,
)


def test_parse_redact_columns_none_returns_none():
    assert parse_redact_columns(None) is None


def test_parse_redact_columns_empty_string_returns_none():
    assert parse_redact_columns("") is None


def test_parse_redact_columns_single():
    cfg = parse_redact_columns("password")
    assert cfg.columns == ["password"]


def test_parse_redact_columns_multiple():
    cfg = parse_redact_columns("password, token, secret")
    assert cfg.columns == ["password", "token", "secret"]


def test_parse_redact_columns_raises_on_empty_entry():
    with pytest.raises(RedactError):
        parse_redact_columns("password,,token")


def test_validate_redact_columns_passes_when_present():
    cfg = RedactConfig(columns=["password"])
    validate_redact_columns(cfg, ["id", "name", "password"])


def test_validate_redact_columns_raises_on_missing():
    cfg = RedactConfig(columns=["ghost"])
    with pytest.raises(RedactError, match="ghost"):
        validate_redact_columns(cfg, ["id", "name"])


def _cfg(*cols):
    return RedactConfig(columns=list(cols))


def test_redact_event_masks_added_row():
    event = RowAdded(key="1", row={"id": "1", "password": "secret"})
    result = redact_event(event, _cfg("password"))
    assert result.row["password"] == "***"
    assert result.row["id"] == "1"


def test_redact_event_masks_removed_row():
    event = RowRemoved(key="1", row={"id": "1", "token": "abc"})
    result = redact_event(event, _cfg("token"))
    assert result.row["token"] == "***"


def test_redact_event_masks_modified_row():
    event = RowModified(
        key="1",
        before={"id": "1", "password": "old"},
        after={"id": "1", "password": "new"},
    )
    result = redact_event(event, _cfg("password"))
    assert result.before["password"] == "***"
    assert result.after["password"] == "***"


def test_redact_diff_none_config_returns_unchanged():
    events = [RowAdded(key="1", row={"id": "1", "pw": "secret"})]
    assert redact_diff(events, None) is events


def test_redact_diff_applies_to_all_events():
    events = [
        RowAdded(key="1", row={"id": "1", "pw": "s1"}),
        RowRemoved(key="2", row={"id": "2", "pw": "s2"}),
    ]
    result = redact_diff(events, _cfg("pw"))
    assert all(e.row["pw"] == "***" for e in result)
