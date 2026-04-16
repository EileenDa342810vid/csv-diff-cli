import argparse
import pytest
from csv_diff.threshold_cli import add_threshold_arguments, apply_threshold
from csv_diff.stats import DiffStats


def _stats(added=0, removed=0, modified=0, unchanged=0):
    return DiffStats(added=added, removed=removed, modified=modified, unchanged=unchanged, modified_columns=[])


def _args(threshold=None):
    parser = argparse.ArgumentParser()
    add_threshold_arguments(parser)
    return parser.parse_args([] if threshold is None else ["--threshold", str(threshold)])


def test_add_threshold_arguments_adds_flag():
    parser = argparse.ArgumentParser()
    add_threshold_arguments(parser)
    args = parser.parse_args(["--threshold", "5"])
    assert args.threshold == "5"


def test_no_threshold_with_changes_exits_one():
    args = _args()
    _, code = apply_threshold(args, _stats(added=1), "some output")
    assert code == 1


def test_no_threshold_no_changes_exits_zero():
    args = _args()
    _, code = apply_threshold(args, _stats(), "")
    assert code == 0


def test_threshold_not_met_exits_zero():
    args = _args(threshold=5)
    _, code = apply_threshold(args, _stats(added=2), "output")
    assert code == 0


def test_threshold_not_met_returns_description():
    args = _args(threshold=5)
    text, _ = apply_threshold(args, _stats(added=2), "output")
    assert "suppressed" in text


def test_threshold_met_returns_original_output():
    args = _args(threshold=3)
    text, code = apply_threshold(args, _stats(added=3), "my output")
    assert text == "my output"
    assert code == 1


def test_invalid_threshold_returns_exit_2():
    args = _args(threshold="bad")
    _, code = apply_threshold(args, _stats(), "")
    assert code == 2
