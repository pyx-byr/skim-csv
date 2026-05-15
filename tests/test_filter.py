"""Tests for skim_csv.filter module."""

import pytest

from skim_csv.filter import RowFilter, apply_filters, parse_filter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def rows():
    return [
        {"name": "Alice", "age": "30", "city": "London"},
        {"name": "Bob", "age": "25", "city": "Paris"},
        {"name": "Carol", "age": "35", "city": "London"},
        {"name": "Dave", "age": "25", "city": "Berlin"},
    ]


# ---------------------------------------------------------------------------
# parse_filter
# ---------------------------------------------------------------------------

def test_parse_filter_valid():
    f = parse_filter("age:gte:30")
    assert f.column == "age"
    assert f.op == "gte"
    assert f.value == "30"


def test_parse_filter_invalid_format():
    with pytest.raises(ValueError, match="column:op:value"):
        parse_filter("age-gte-30")


def test_parse_filter_unknown_op():
    with pytest.raises(ValueError, match="Unknown operator"):
        parse_filter("age:between:10")


# ---------------------------------------------------------------------------
# RowFilter.matches
# ---------------------------------------------------------------------------

def test_filter_eq(rows):
    f = RowFilter("city", "eq", "London")
    result = [r for r in rows if f.matches(r)]
    assert len(result) == 2
    assert all(r["city"] == "London" for r in result)


def test_filter_ne(rows):
    f = RowFilter("city", "ne", "London")
    result = [r for r in rows if f.matches(r)]
    assert len(result) == 2


def test_filter_gt(rows):
    f = RowFilter("age", "gt", "25")
    result = [r for r in rows if f.matches(r)]
    assert {r["name"] for r in result} == {"Alice", "Carol"}


def test_filter_lte(rows):
    f = RowFilter("age", "lte", "25")
    result = [r for r in rows if f.matches(r)]
    assert {r["name"] for r in result} == {"Bob", "Dave"}


def test_filter_contains(rows):
    f = RowFilter("name", "contains", "o")
    result = [r for r in rows if f.matches(r)]
    assert {r["name"] for r in result} == {"Bob", "Carol"}


def test_filter_startswith(rows):
    f = RowFilter("name", "startswith", "A")
    result = [r for r in rows if f.matches(r)]
    assert len(result) == 1 and result[0]["name"] == "Alice"


def test_filter_non_numeric_comparison_returns_false(rows):
    f = RowFilter("name", "gt", "10")
    # 'Alice' is not numeric — should return False, not raise
    assert f.matches(rows[0]) is False


def test_filter_missing_column(rows):
    f = RowFilter("salary", "eq", "1000")
    result = [r for r in rows if f.matches(r)]
    assert result == []


# ---------------------------------------------------------------------------
# apply_filters
# ---------------------------------------------------------------------------

def test_apply_filters_no_filters(rows):
    result = list(apply_filters(rows, filters=None))
    assert result == rows


def test_apply_filters_empty_list(rows):
    result = list(apply_filters(rows, filters=[]))
    assert result == rows


def test_apply_filters_single(rows):
    filters = [RowFilter("city", "eq", "London")]
    result = list(apply_filters(rows, filters))
    assert len(result) == 2


def test_apply_filters_multiple_and_logic(rows):
    filters = [
        RowFilter("city", "eq", "London"),
        RowFilter("age", "gte", "35"),
    ]
    result = list(apply_filters(rows, filters))
    assert len(result) == 1
    assert result[0]["name"] == "Carol"


def test_apply_filters_no_match(rows):
    filters = [RowFilter("age", "gt", "100")]
    result = list(apply_filters(rows, filters))
    assert result == []
