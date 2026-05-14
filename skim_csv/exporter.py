"""Export column profiles to JSON or CSV summary formats."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from skim_csv.profiler import ColumnProfile


def profile_to_dict(profile: ColumnProfile) -> dict:
    """Convert a ColumnProfile to a plain dictionary."""
    from skim_csv.profiler import null_rate, mean, is_numeric

    return {
        "column": profile.name,
        "count": profile.count,
        "null_count": profile.null_count,
        "null_rate": round(null_rate(profile), 4),
        "numeric": is_numeric(profile),
        "min": profile.min_val,
        "max": profile.max_val,
        "mean": round(mean(profile), 4) if is_numeric(profile) else None,
        "unique_approx": len(profile.sample_values),
        "sample_values": list(profile.sample_values)[:5],
    }


def export_json(profiles: List[ColumnProfile], indent: int = 2) -> str:
    """Serialize profiles to a JSON string."""
    data = [profile_to_dict(p) for p in profiles]
    return json.dumps(data, indent=indent, default=str)


def export_csv(profiles: List[ColumnProfile]) -> str:
    """Serialize profiles to a CSV summary string."""
    if not profiles:
        return ""

    fieldnames = [
        "column", "count", "null_count", "null_rate",
        "numeric", "min", "max", "mean", "unique_approx",
    ]

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for profile in profiles:
        row = profile_to_dict(profile)
        writer.writerow(row)

    return buf.getvalue()


def export_profiles(profiles: List[ColumnProfile], fmt: str) -> str:
    """Dispatch export based on format string ('json' or 'csv')."""
    fmt = fmt.lower().strip()
    if fmt == "json":
        return export_json(profiles)
    elif fmt == "csv":
        return export_csv(profiles)
    else:
        raise ValueError(f"Unsupported export format: {fmt!r}. Use 'json' or 'csv'.")
