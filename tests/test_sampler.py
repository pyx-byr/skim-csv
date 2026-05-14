"""Tests for skim_csv.sampler."""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path

import pytest

from skim_csv.sampler import reservoir_sample, sample_to_dicts


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def small_csv(tmp_path: Path) -> str:
    """CSV with a header and 20 data rows."""
    filepath = tmp_path / "small.csv"
    with filepath.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "value", "label"])
        for i in range(20):
            writer.writerow([str(i), str(i * 1.5), f"item_{i}"])
    return str(filepath)


@pytest.fixture()
def headerless_csv(tmp_path: Path) -> str:
    """CSV without a header row."""
    filepath = tmp_path / "noheader.csv"
    with filepath.open("w", newline="") as fh:
        writer = csv.writer(fh)
        for i in range(10):
            writer.writerow([str(i), str(i + 100)])
    return str(filepath)


@pytest.fixture()
def large_csv(tmp_path: Path) -> str:
    """CSV with a header and 1 000 data rows for statistical tests."""
    filepath = tmp_path / "large.csv"
    with filepath.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["idx"])
        for i in range(1000):
            writer.writerow([str(i)])
    return str(filepath)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_reservoir_sample_returns_headers(small_csv: str) -> None:
    headers, sample = reservoir_sample(small_csv, n=5, seed=0)
    assert headers == ["id", "value", "label"]


def test_reservoir_sample_size_capped_by_file(small_csv: str) -> None:
    """Asking for more rows than exist should return all data rows."""
    headers, sample = reservoir_sample(small_csv, n=50, seed=0)
    assert len(sample) == 20


def test_reservoir_sample_exact_n(small_csv: str) -> None:
    headers, sample = reservoir_sample(small_csv, n=5, seed=42)
    assert len(sample) == 5


def test_reservoir_sample_reproducible(small_csv: str) -> None:
    _, s1 = reservoir_sample(small_csv, n=10, seed=7)
    _, s2 = reservoir_sample(small_csv, n=10, seed=7)
    assert s1 == s2


def test_reservoir_sample_different_seeds(large_csv: str) -> None:
    _, s1 = reservoir_sample(large_csv, n=50, seed=1)
    _, s2 = reservoir_sample(large_csv, n=50, seed=2)
    # With 1 000 rows and n=50, two different seeds should differ.
    assert s1 != s2


def test_reservoir_sample_no_header(headerless_csv: str) -> None:
    headers, sample = reservoir_sample(headerless_csv, n=5, has_header=False, seed=0)
    assert headers == []
    assert len(sample) == 5


def test_sample_to_dicts_with_headers(small_csv: str) -> None:
    headers, sample = reservoir_sample(small_csv, n=5, seed=0)
    records = sample_to_dicts(headers, sample)
    assert len(records) == 5
    assert set(records[0].keys()) == {"id", "value", "label"}


def test_sample_to_dicts_no_headers(headerless_csv: str) -> None:
    headers, sample = reservoir_sample(headerless_csv, n=3, has_header=False, seed=0)
    records = sample_to_dicts(headers, sample)
    assert len(records) == 3
    # Keys should be stringified column indices.
    assert "0" in records[0] and "1" in records[0]


def test_empty_csv_returns_empty(tmp_path: Path) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    headers, sample = reservoir_sample(str(empty), n=10, seed=0)
    assert headers == []
    assert sample == []
