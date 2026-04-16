import pytest
from csv_diff.threshold import (
    ThresholdError,
    ThresholdConfig,
    parse_threshold,
    exceeds_threshold,
    describe_threshold,
)
from csv_diff.stats import DiffStats


def _stats(added=0, removed=0, modified=0):
    return DiffStats(added=added, removed=removed, modified=modified, unchanged=0, modified_columns=[])


def test_parse_threshold_none_returns_none():
    assert parse_threshold(None) is None


def test_parse_threshold_integer_passthrough():
    cfg = parse_threshold(5)
    assert cfg.min_changes == 5


def test_parse_threshold_string_integer():
    cfg = parse_threshold("3")
    assert cfg.min_changes == 3


def test_parse_threshold_raises_on_non_integer():
    with pytest.raises(ThresholdError):
        parse_threshold("abc")


def test_parse_threshold_raises_on_zero():
    with pytest.raises(ThresholdError):
        parse_threshold(0)


def test_parse_threshold_raises_on_negative():
    with pytest.raises(ThresholdError):
        parse_threshold(-1)


def test_exceeds_threshold_no_config_always_true():
    assert exceeds_threshold(_stats(), None) is True


def test_exceeds_threshold_below_limit():
    cfg = ThresholdConfig(min_changes=5)
    assert exceeds_threshold(_stats(added=2, removed=1), cfg) is False


def test_exceeds_threshold_at_limit():
    cfg = ThresholdConfig(min_changes=3)
    assert exceeds_threshold(_stats(added=2, removed=1), cfg) is True


def test_exceeds_threshold_above_limit():
    cfg = ThresholdConfig(min_changes=2)
    assert exceeds_threshold(_stats(added=3), cfg) is True


def test_describe_threshold_contains_counts():
    cfg = ThresholdConfig(min_changes=10)
    msg = describe_threshold(cfg, _stats(added=2, removed=1))
    assert "3" in msg
    assert "10" in msg
