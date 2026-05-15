"""Tests for skim_csv.differ and skim_csv.diff_formatter."""

from __future__ import annotations

import pytest

from skim_csv.profiler import ColumnProfile, update
from skim_csv.differ import diff_profiles, ColumnDiff
from skim_csv.diff_formatter import render_diff_table


def _make_profile(values: list) -> ColumnProfile:
    p = ColumnProfile()
    for v in values:
        update(p, v)
    return p


@pytest.fixture()
def left_profiles():
    return {
        "age": _make_profile(["25", "30", "", "45"]),
        "name": _make_profile(["Alice", "Bob", "Carol"]),
        "score": _make_profile(["10", "20", "30"]),
    }


@pytest.fixture()
def right_profiles():
    return {
        "age": _make_profile(["28", "33", "40"]),
        "name": _make_profile(["Dave", "", "Eve"]),
        "city": _make_profile(["NY", "LA", "SF"]),
    }


def test_diff_returns_all_columns(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    names = {d.name for d in diffs}
    assert names == {"age", "name", "score", "city"}


def test_diff_only_in_left(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    score_diff = next(d for d in diffs if d.name == "score")
    assert score_diff.only_in_left
    assert not score_diff.only_in_right


def test_diff_only_in_right(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    city_diff = next(d for d in diffs if d.name == "city")
    assert city_diff.only_in_right
    assert not city_diff.only_in_left


def test_diff_null_rate_delta(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    age_diff = next(d for d in diffs if d.name == "age")
    assert age_diff.null_rate_delta is not None
    # left age has 1 null out of 4; right has none
    assert age_diff.null_rate_left == pytest.approx(0.25)
    assert age_diff.null_rate_right == pytest.approx(0.0)


def test_diff_mean_delta_none_for_missing_column(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    score_diff = next(d for d in diffs if d.name == "score")
    assert score_diff.mean_delta is None


def test_diff_sorted_by_name(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    names = [d.name for d in diffs]
    assert names == sorted(names)


def test_render_diff_table_contains_headers(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    table = render_diff_table(diffs)
    assert "column" in table
    assert "null%_L" in table
    assert "mean_R" in table


def test_render_diff_table_contains_column_names(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    table = render_diff_table(diffs)
    assert "age" in table
    assert "city" in table
    assert "score" in table


def test_render_diff_table_missing_column_shows_dash(left_profiles, right_profiles):
    diffs = diff_profiles(left_profiles, right_profiles)
    table = render_diff_table(diffs)
    # score only in left, so right mean should be "-"
    lines = table.splitlines()
    score_line = next(l for l in lines if "score" in l)
    assert "-" in score_line
