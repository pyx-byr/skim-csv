"""Render a correlation table for the terminal."""

from __future__ import annotations

from typing import List

from .correlator import ColumnCorrelation

_COL_WIDTHS = {"col_a": 18, "col_b": 18, "r": 10, "n": 8}
_HEADERS = ["Column A", "Column B", "r", "n"]
_KEYS = ["col_a", "col_b", "r", "n"]


def _separator() -> str:
    parts = ["-" * w for w in _COL_WIDTHS.values()]
    return "+" + "+".join(parts) + "+"


def _header_row() -> str:
    cells = [
        h.ljust(w)
        for h, w in zip(_HEADERS, _COL_WIDTHS.values())
    ]
    return "|" + "|".join(cells) + "|"


def _corr_row(c: ColumnCorrelation) -> str:
    widths = list(_COL_WIDTHS.values())
    values = [
        c.col_a[:widths[0]].ljust(widths[0]),
        c.col_b[:widths[1]].ljust(widths[1]),
        f"{c.r:+.4f}".rjust(widths[2]),
        str(c.n).rjust(widths[3]),
    ]
    return "|" + "|".join(values) + "|"


def render_correlation_table(correlations: List[ColumnCorrelation]) -> str:
    """Return a formatted ASCII table of correlations."""
    if not correlations:
        return "No numeric column pairs found for correlation."

    sep = _separator()
    lines = [sep, _header_row(), sep]
    for c in correlations:
        lines.append(_corr_row(c))
    lines.append(sep)
    return "\n".join(lines)
