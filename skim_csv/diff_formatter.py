"""Render a diff result as a human-readable table."""

from __future__ import annotations

from typing import List

from skim_csv.differ import ColumnDiff

_COL_WIDTHS = [20, 8, 8, 10, 10, 12, 12, 10, 10]
_HEADERS = ["column", "in_left", "in_right", "rows_L", "rows_R",
            "null%_L", "null%_R", "mean_L", "mean_R"]


def _fmt(value: object, width: int) -> str:
    text = "-" if value is None else str(value)
    return text[:width].ljust(width)


def _separator(widths: List[int]) -> str:
    return "+" + "+".join("-" * (w + 2) for w in widths) + "+"


def _row(cells: List[str], widths: List[int]) -> str:
    parts = [" " + _fmt(c, w) + " " for c, w in zip(cells, widths)]
    return "|" + "|".join(parts) + "|"


def render_diff_table(diffs: List[ColumnDiff]) -> str:
    """Return a formatted string table of column diffs."""
    sep = _separator(_COL_WIDTHS)
    lines = [sep, _row(_HEADERS, _COL_WIDTHS), sep]

    for d in diffs:
        nr_l = f"{d.null_rate_left:.1%}" if d.null_rate_left is not None else None
        nr_r = f"{d.null_rate_right:.1%}" if d.null_rate_right is not None else None
        m_l = f"{d.mean_left:.2f}" if d.mean_left is not None else None
        m_r = f"{d.mean_right:.2f}" if d.mean_right is not None else None

        cells = [
            d.name,
            "yes" if d.in_left else "no",
            "yes" if d.in_right else "no",
            str(d.row_count_left) if d.row_count_left is not None else "-",
            str(d.row_count_right) if d.row_count_right is not None else "-",
            nr_l or "-",
            nr_r or "-",
            m_l or "-",
            m_r or "-",
        ]
        lines.append(_row(cells, _COL_WIDTHS))

    lines.append(sep)
    return "\n".join(lines)
