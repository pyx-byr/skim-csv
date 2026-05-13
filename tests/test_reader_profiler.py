"""Tests for the streaming reader and column profiler."""

from __future__ import annotations

import csv
import textwrap
from pathlib import Path

import pytest

from skim_csv.profiler import ColumnProfile, profile_chunks
from skim_csv.reader import detect_headers, iter_rows, stream_csv


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    data = textwrap.dedent("""\
        name,age,score
        Alice,30,9.5
        Bob,25,8.0
        Carol,,7.5
        Dave,40,
        Eve,35,6.0
    """)
    p = tmp_path / "sample.csv"
    p.write_text(data, encoding="utf-8")
    return p


def test_stream_csv_yields_chunks(sample_csv: Path) -> None:
    chunks = list(stream_csv(sample_csv, chunk_size=2))
    assert len(chunks) == 3  # 2 + 2 + 1
    assert all(isinstance(c, list) for c in chunks)
    assert all(isinstance(r, dict) for c in chunks for r in c)


def test_iter_rows_count(sample_csv: Path) -> None:
    rows = list(iter_rows(sample_csv))
    assert len(rows) == 5


def test_detect_headers(sample_csv: Path) -> None:
    headers = detect_headers(sample_csv)
    assert headers == ["name", "age", "score"]


def test_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        list(stream_csv("/nonexistent/path/file.csv"))


def test_empty_file_raises(tmp_path: Path) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    with pytest.raises(ValueError, match="empty"):
        list(stream_csv(empty))


def test_column_profile_numeric() -> None:
    p = ColumnProfile(name="age")
    for v in ["30", "25", "40", ""]:
        p.update(v)
    assert p.count == 4
    assert p.null_count == 1
    assert p.numeric_count == 3
    assert p.min_value == 25.0
    assert p.max_value == 40.0
    assert abs(p.mean - 31.666) < 0.01
    assert not p.is_numeric  # has a null


def test_column_profile_non_numeric() -> None:
    p = ColumnProfile(name="name")
    for v in ["Alice", "Bob", "Carol"]:
        p.update(v)
    assert p.is_numeric is False
    assert p.mean is None


def test_profile_chunks_integration(sample_csv: Path) -> None:
    chunks = stream_csv(sample_csv)
    profiles = profile_chunks(chunks)
    assert set(profiles.keys()) == {"name", "age", "score"}
    assert profiles["name"].count == 5
    assert profiles["age"].null_count == 1
    assert profiles["score"].null_count == 1
