"""High-level pipeline: read → filter → profile.

Ties together reader, filter, and profiler so the CLI and tests
can drive the full workflow through a single entry-point.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from skim_csv.filter import RowFilter, apply_filters
from skim_csv.profiler import ColumnProfile, update, null_rate, mean
from skim_csv.reader import iter_rows


def profile_file(
    path: str | Path,
    filters: Optional[List[RowFilter]] = None,
    chunk_size: int = 1_000,
    encoding: str = "utf-8",
) -> Dict[str, ColumnProfile]:
    """Stream *path*, apply *filters*, and return per-column profiles.

    Parameters
    ----------
    path:
        CSV file to read.
    filters:
        Optional list of :class:`RowFilter` predicates (AND logic).
    chunk_size:
        Number of rows per read chunk passed to the underlying reader.
    encoding:
        File encoding.

    Returns
    -------
    dict mapping column name → :class:`ColumnProfile`
    """
    profiles: Dict[str, ColumnProfile] = {}

    raw_rows = iter_rows(path, chunk_size=chunk_size, encoding=encoding)
    filtered_rows = apply_filters(raw_rows, filters=filters)

    for row in filtered_rows:
        for col, value in row.items():
            if col not in profiles:
                profiles[col] = ColumnProfile(name=col)
            update(profiles[col], value)

    return profiles


def summarise(
    profiles: Dict[str, ColumnProfile],
) -> List[Dict[str, object]]:
    """Convert profile objects to plain dicts suitable for display/export."""
    summary = []
    for col, prof in profiles.items():
        summary.append(
            {
                "column": col,
                "count": prof.count,
                "null_rate": round(null_rate(prof), 4),
                "mean": mean(prof),
                "min": prof.min_val,
                "max": prof.max_val,
                "unique": prof.unique_count,
            }
        )
    return summary
