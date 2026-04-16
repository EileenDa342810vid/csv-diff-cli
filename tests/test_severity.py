"""Tests for csv_diff.severity."""
import pytest
from csv_diff.severity import (
    SeverityConfig,
    SeverityError,
    classify,
    format_severity,
    parse_severity_config,
)
from csv_diff.stats import DiffStats


def _stats(added=0, removed=0, modified=0):
    return DiffStats(added=added, removed=removed, modified=modified, unchanged=0)


def test_parse_severity_config_defaults():
    cfg = parse_severity_config()
    assert cfg == SeverityConfig(low=1, medium=10, high=50)


def test_parse_severity_config_custom():
    cfg = parse_severity_config(low=2, medium=20, high=100)
    assert cfg.low == 2 and cfg.medium == 20 and cfg.high == 100


def test_parse_severity_config_raises_when_low_exceeds_medium():
    with pytest.raises(SeverityError):
        parse_severity_config(low=20, medium=10, high=50)


def test_parse_severity_config_raises_when_medium_exceeds_high():
    with pytest.raises(SeverityError):
        parse_severity_config(low=1, medium=60, high=50)


def test_parse_severity_config_raises_on_zero_low():
    with pytest.raises(SeverityError):
        parse_severity_config(low=0, medium=10, high=50)


def test_classify_none_when_no_changes():
    assert classify(_stats()) == "none"


def test_classify_low_for_small_changes():
    assert classify(_stats(added=3)) == "low"


def test_classify_medium_at_boundary():
    assert classify(_stats(added=10)) == "medium"


def test_classify_high_at_boundary():
    assert classify(_stats(added=50)) == "high"


def test_classify_uses_custom_config():
    cfg = SeverityConfig(low=1, medium=5, high=20)
    assert classify(_stats(added=6), cfg) == "medium"
    assert classify(_stats(added=20), cfg) == "high"


def test_format_severity_none():
    assert "No changes" in format_severity("none")


def test_format_severity_high():
    assert "High" in format_severity("high")


def test_format_severity_unknown():
    result = format_severity("critical")
    assert "Unknown" in result
