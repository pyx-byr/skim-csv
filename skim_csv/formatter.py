"""Render profiling results as a human-readable table."""

from __future__ import annotations

from skim_csv.profiler import ColumnProfile

_COL_WIDTHS = {
    "column": 20,
    "count": 8,
    "nulls": 8,
    "null%": 8,
    "numeric": 9,
    "min": 12,
    "max": 12,
    "mean": 12,
    "sample": 30,
}


def _fmt(value: object, width: int) -> str:
    return str(value)[:width].ljust(width)


def _header_row() -> str:
    return "  ".join(_fmt(k.upper(), v) for k, v in _COL_WIDTHS.items())


def _separator() -> str:
    return "  ".join("-" * w for w in _COL_WIDTHS.values())


def _profile_row(profile: ColumnProfile) -> str:
    mean_str = f"{profile.mean:.4f}" if profile.mean is not None else "—"
    min_str = f"{profile.min_value:.4f}" if profile.min_value is not None else "—"
    max_str = f"{profile.max_value:.4f}" if profile.max_value is not None else "—"
    sample_str = ", ".join(profile.sample_values[:3])

    cells = [
        _fmt(profile.name, _COL_WIDTHS["column"]),
        _fmt(profile.count, _COL_WIDTHS["count"]),
        _fmt(profile.null_count, _COL_WIDTHS["nulls"]),
        _fmt(f"{profile.null_rate:.1%}", _COL_WIDTHS["null%"]),
        _fmt("yes" if profile.is_numeric else "no", _COL_WIDTHS["numeric"]),
        _fmt(min_str, _COL_WIDTHS["min"]),
        _fmt(max_str, _COL_WIDTHS["max"]),
        _fmt(mean_str, _COL_WIDTHS["mean"]),
        _fmt(sample_str, _COL_WIDTHS["sample"]),
    ]
    return "  ".join(cells)


def render_table(profiles: dict[str, ColumnProfile], total_rows: int) -> str:
    lines = [
        f"Rows processed : {total_rows:,}",
        f"Columns found  : {len(profiles)}",
        "",
        _header_row(),
        _separator(),
    ]
    for profile in profiles.values():
        lines.append(_profile_row(profile))
    return "\n".join(lines)
