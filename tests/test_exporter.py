"""Tests for skim_csv.exporter — JSON and CSV profile export."""

from __future__ import annotations

import csv
import io
import json

import pytest

from skim_csv.profiler import ColumnProfile, update
from skim_csv.exporter import (
    profile_to_dict,
    export_json,
    export_csv,
    export_profiles,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def numeric_profile() -> ColumnProfile:
    p = ColumnProfile(name="age")
    for val in ["25", "30", "", "45", "22"]:
        update(p, val)
    return p


@pytest.fixture()
def text_profile() -> ColumnProfile:
    p = ColumnProfile(name="city")
    for val in ["Berlin", "Paris", "", "Tokyo"]:
        update(p, val)
    return p


# ---------------------------------------------------------------------------
# profile_to_dict
# ---------------------------------------------------------------------------

def test_profile_to_dict_keys(numeric_profile):
    d = profile_to_dict(numeric_profile)
    expected_keys = {"column", "count", "null_count", "null_rate",
                     "numeric", "min", "max", "mean", "unique_approx", "sample_values"}
    assert expected_keys == set(d.keys())


def test_profile_to_dict_numeric_values(numeric_profile):
    d = profile_to_dict(numeric_profile)
    assert d["column"] == "age"
    assert d["count"] == 5
    assert d["null_count"] == 1
    assert d["numeric"] is True
    assert d["mean"] == pytest.approx(30.5, rel=1e-3)


def test_profile_to_dict_text_mean_is_none(text_profile):
    d = profile_to_dict(text_profile)
    assert d["numeric"] is False
    assert d["mean"] is None


# ---------------------------------------------------------------------------
# export_json
# ---------------------------------------------------------------------------

def test_export_json_valid(numeric_profile, text_profile):
    result = export_json([numeric_profile, text_profile])
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["column"] == "age"
    assert parsed[1]["column"] == "city"


def test_export_json_empty():
    result = export_json([])
    assert json.loads(result) == []


# ---------------------------------------------------------------------------
# export_csv
# ---------------------------------------------------------------------------

def test_export_csv_has_header(numeric_profile):
    result = export_csv([numeric_profile])
    reader = csv.DictReader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["column"] == "age"
    assert rows[0]["numeric"] == "True"


def test_export_csv_empty():
    assert export_csv([]) == ""


# ---------------------------------------------------------------------------
# export_profiles dispatch
# ---------------------------------------------------------------------------

def test_export_profiles_json(numeric_profile):
    out = export_profiles([numeric_profile], "json")
    assert json.loads(out)[0]["column"] == "age"


def test_export_profiles_csv(numeric_profile):
    out = export_profiles([numeric_profile], "csv")
    assert "age" in out


def test_export_profiles_invalid_format(numeric_profile):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_profiles([numeric_profile], "xml")
