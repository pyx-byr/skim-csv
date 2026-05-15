"""Tests for skim_csv.sorter."""

from __future__ import annotations

import pytest

from skim_csv.profiler import ColumnProfile
from skim_csv.sorter import sort_profiles, top_n, _SORT_KEYS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_profile(name: str, count: int, nulls: int, values=None) -> ColumnProfile:
    p = ColumnProfile(name=name)
    p.count = count
    p.null_count = nulls
    if values:
        p.numeric_values = values
        p.min_val = min(values)
        p.max_val = max(values)
    p.unique_count = len(set(values)) if values else 0
    return p


@pytest.fixture()
def profiles():
    return [
        _make_profile("age", 100, 5, [20.0, 30.0, 40.0]),
        _make_profile("score", 100, 20, [1.0, 2.0, 3.0, 4.0]),
        _make_profile("name", 100, 0, []),
        _make_profile("zip", 80, 10, [10000.0, 20000.0]),
    ]


# ---------------------------------------------------------------------------
# sort_profiles
# ---------------------------------------------------------------------------


def test_sort_by_name_ascending(profiles):
    result = sort_profiles(profiles, key="name")
    assert [p.name for p in result] == ["age", "name", "score", "zip"]


def test_sort_by_name_descending(profiles):
    result = sort_profiles(profiles, key="name", reverse=True)
    assert result[0].name == "zip"


def test_sort_by_null_rate_descending(profiles):
    result = sort_profiles(profiles, key="null_rate", reverse=True)
    # score has 20/100 = 0.20, zip has 10/80 = 0.125, age has 5/100 = 0.05
    assert result[0].name == "score"
    assert result[1].name == "zip"


def test_sort_by_count_ascending(profiles):
    result = sort_profiles(profiles, key="count")
    assert result[0].name == "zip"  # count=80


def test_sort_by_mean(profiles):
    result = sort_profiles(profiles, key="mean")
    # name has no numeric values -> mean is None, pushed to end
    names = [p.name for p in result]
    assert names[-1] == "name"  # None mean last
    assert names[0] == "score"  # mean=2.5 is lowest numeric mean


def test_sort_by_unique(profiles):
    result = sort_profiles(profiles, key="unique")
    assert result[0].name == "name"  # unique_count=0


def test_sort_invalid_key(profiles):
    with pytest.raises(ValueError, match="Unknown sort key"):
        sort_profiles(profiles, key="nonexistent")


def test_sort_preserves_all_profiles(profiles):
    result = sort_profiles(profiles, key="count")
    assert len(result) == len(profiles)


# ---------------------------------------------------------------------------
# top_n
# ---------------------------------------------------------------------------


def test_top_n_returns_correct_count(profiles):
    result = top_n(profiles, n=2, key="null_rate")
    assert len(result) == 2


def test_top_n_highest_null_rate_first(profiles):
    result = top_n(profiles, n=1, key="null_rate")
    assert result[0].name == "score"


def test_top_n_capped_by_total(profiles):
    result = top_n(profiles, n=100, key="null_rate")
    assert len(result) == len(profiles)


def test_top_n_empty_list():
    assert top_n([], n=3, key="null_rate") == []
