"""Tests for skim_csv.correlator and skim_csv.correlation_formatter."""

from __future__ import annotations

import math
import pytest

from skim_csv.correlator import (
    ColumnCorrelation,
    _pearson,
    correlate_columns,
    top_correlations,
)
from skim_csv.correlation_formatter import render_correlation_table
from skim_csv.profiler import ColumnProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_profile(name: str, numeric: bool) -> ColumnProfile:
    p = ColumnProfile(name)
    if numeric:
        p.is_numeric = True
        p.count = 5
    return p


ROWS = [
    {"x": "1", "y": "2", "z": "foo"},
    {"x": "2", "y": "4", "z": "bar"},
    {"x": "3", "y": "6", "z": "baz"},
    {"x": "4", "y": "8", "z": "qux"},
    {"x": "5", "y": "10", "z": "quux"},
]

PROFILES = [
    _make_profile("x", numeric=True),
    _make_profile("y", numeric=True),
    _make_profile("z", numeric=False),
]


# ---------------------------------------------------------------------------
# _pearson
# ---------------------------------------------------------------------------

def test_pearson_perfect_positive():
    pairs = [(1, 2), (2, 4), (3, 6), (4, 8)]
    r, n = _pearson(pairs)
    assert r is not None
    assert math.isclose(r, 1.0, abs_tol=1e-9)
    assert n == 4


def test_pearson_too_few_points():
    r, n = _pearson([(1, 2)])
    assert r is None
    assert n == 1


def test_pearson_zero_variance():
    pairs = [(3, 1), (3, 2), (3, 3)]
    r, n = _pearson(pairs)
    assert r is None


# ---------------------------------------------------------------------------
# correlate_columns
# ---------------------------------------------------------------------------

def test_correlate_columns_only_numeric_pairs():
    results = correlate_columns(ROWS, PROFILES)
    assert all(isinstance(c, ColumnCorrelation) for c in results)
    col_names = {(c.col_a, c.col_b) for c in results}
    assert ("x", "y") in col_names
    # z is not numeric — must not appear
    assert all("z" not in (c.col_a, c.col_b) for c in results)


def test_correlate_columns_perfect_r():
    results = correlate_columns(ROWS, PROFILES)
    assert len(results) == 1
    assert math.isclose(results[0].r, 1.0, abs_tol=1e-9)


def test_correlate_columns_skips_bad_values():
    rows = [
        {"x": "1", "y": "N/A"},
        {"x": "2", "y": "4"},
        {"x": "3", "y": "6"},
    ]
    profiles = [_make_profile("x", True), _make_profile("y", True)]
    results = correlate_columns(rows, profiles)
    assert results[0].n == 2  # only 2 valid pairs


# ---------------------------------------------------------------------------
# top_correlations
# ---------------------------------------------------------------------------

def test_top_correlations_limits_results():
    corrs = [
        ColumnCorrelation("a", "b", 0.9, 10),
        ColumnCorrelation("a", "c", -0.8, 10),
        ColumnCorrelation("b", "c", 0.3, 10),
    ]
    top = top_correlations(corrs, n=2)
    assert len(top) == 2
    assert top[0].col_a == "a" and top[0].col_b == "b"


# ---------------------------------------------------------------------------
# render_correlation_table
# ---------------------------------------------------------------------------

def test_render_empty_correlations():
    out = render_correlation_table([])
    assert "No numeric" in out


def test_render_table_contains_column_names():
    corrs = [ColumnCorrelation("x", "y", 0.9999, 5)]
    out = render_correlation_table(corrs)
    assert "x" in out
    assert "y" in out
    assert "+0.9999" in out
