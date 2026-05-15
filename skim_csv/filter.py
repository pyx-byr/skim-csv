"""Row-level filtering for skim-csv.

Allows users to apply simple column-value predicates before profiling,
so only matching rows are counted/profiled.
"""

from __future__ import annotations

import operator
from typing import Callable, Dict, Iterable, List, Optional

# Supported comparison operators
_OPS: Dict[str, Callable[[str, str], bool]] = {
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "gt": lambda a, b: _safe_float(a) > _safe_float(b),
    "lt": lambda a, b: _safe_float(a) < _safe_float(b),
    "gte": lambda a, b: _safe_float(a) >= _safe_float(b),
    "lte": lambda a, b: _safe_float(a) <= _safe_float(b),
    "contains": lambda a, b: b in a,
    "startswith": lambda a, b: a.startswith(b),
}


def _safe_float(value: str) -> float:
    """Convert to float or raise ValueError with a clear message."""
    try:
        return float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Cannot compare non-numeric value: {value!r}") from exc


class RowFilter:
    """A single predicate: column OP value."""

    def __init__(self, column: str, op: str, value: str) -> None:
        if op not in _OPS:
            raise ValueError(
                f"Unknown operator {op!r}. Choose from: {list(_OPS)}"
            )
        self.column = column
        self.op = op
        self.value = value
        self._fn = _OPS[op]

    def matches(self, row: Dict[str, str]) -> bool:
        cell = row.get(self.column, "")
        try:
            return self._fn(cell, self.value)
        except ValueError:
            return False

    def __repr__(self) -> str:  # pragma: no cover
        return f"RowFilter({self.column!r} {self.op} {self.value!r})"


def parse_filter(expr: str) -> RowFilter:
    """Parse a filter expression like 'age:gte:30' into a RowFilter."""
    parts = expr.split(":", 2)
    if len(parts) != 3:
        raise ValueError(
            f"Filter expression must be 'column:op:value', got: {expr!r}"
        )
    column, op, value = parts
    return RowFilter(column.strip(), op.strip(), value.strip())


def apply_filters(
    rows: Iterable[Dict[str, str]],
    filters: Optional[List[RowFilter]] = None,
) -> Iterable[Dict[str, str]]:
    """Yield only rows that satisfy ALL filters (AND logic)."""
    if not filters:
        yield from rows
        return
    for row in rows:
        if all(f.matches(row) for f in filters):
            yield row
