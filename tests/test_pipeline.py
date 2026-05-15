"""Integration tests for skim_csv.pipeline."""

import csv
import io
from pathlib import Path

import pytest

from skim_csv.filter import RowFilter
from skim_csv.pipeline import profile_file, summarise


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(tmp_path: Path, rows: list[dict]) -> Path:
    """Write *rows* to a temp CSV and return the path."""
    p = tmp_path / "data.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return p


@pytest.fixture()
def sample_file(tmp_path):
    rows = [
        {"name": "Alice", "age": "30", "score": "88.5"},
        {"name": "Bob", "age": "25", "score": ""},
        {"name": "Carol", "age": "35", "score": "92.0"},
        {"name": "Dave", "age": "25", "score": "76.0"},
        {"name": "Eve", "age": "", "score": "55.5"},
    ]
    return _write_csv(tmp_path, rows)


# ---------------------------------------------------------------------------
# profile_file — no filters
# ---------------------------------------------------------------------------

def test_profile_file_returns_all_columns(sample_file):
    profiles = profile_file(sample_file)
    assert set(profiles.keys()) == {"name", "age", "score"}


def test_profile_file_counts_all_rows(sample_file):
    profiles = profile_file(sample_file)
    assert profiles["name"].count == 5


def test_profile_file_null_rate_age(sample_file):
    from skim_csv.profiler import null_rate
    profiles = profile_file(sample_file)
    # 1 empty age out of 5
    assert null_rate(profiles["age"]) == pytest.approx(0.2)


# ---------------------------------------------------------------------------
# profile_file — with filters
# ---------------------------------------------------------------------------

def test_profile_file_with_eq_filter(sample_file):
    filters = [RowFilter("age", "eq", "25")]
    profiles = profile_file(sample_file, filters=filters)
    # Only Bob and Dave match
    assert profiles["name"].count == 2


def test_profile_file_with_gte_filter(sample_file):
    filters = [RowFilter("age", "gte", "30")]
    profiles = profile_file(sample_file, filters=filters)
    # Alice (30), Carol (35) — Eve has empty age so numeric compare fails
    assert profiles["name"].count == 2


def test_profile_file_combined_filters(sample_file):
    filters = [
        RowFilter("age", "gte", "25"),
        RowFilter("score", "gt", "80"),
    ]
    profiles = profile_file(sample_file, filters=filters)
    # Alice (30, 88.5) and Carol (35, 92.0)
    assert profiles["name"].count == 2


# ---------------------------------------------------------------------------
# summarise
# ---------------------------------------------------------------------------

def test_summarise_keys(sample_file):
    profiles = profile_file(sample_file)
    summary = summarise(profiles)
    assert len(summary) == 3
    expected_keys = {"column", "count", "null_rate", "mean", "min", "max", "unique"}
    for row in summary:
        assert expected_keys == set(row.keys())


def test_summarise_null_rate_rounded(sample_file):
    profiles = profile_file(sample_file)
    summary = {s["column"]: s for s in summarise(profiles)}
    assert summary["age"]["null_rate"] == pytest.approx(0.2)


def test_summarise_no_profiles():
    result = summarise({})
    assert result == []
