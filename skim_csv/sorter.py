"""Sort and rank column profiles by various metrics."""

from __future__ import annotations

from typing import List, Optional

from skim_csv.profiler import ColumnProfile

_SORT_KEYS = ("name", "count", "null_rate", "mean", "min", "max", "unique")


def _profile_sort_key(profile: ColumnProfile, key: str, reverse: bool):
    """Return a sortable value for *key*, placing None last."""
    value = None
    if key == "name":
        value = profile.name
    elif key == "count":
        value = profile.count
    elif key == "null_rate":
        from skim_csv.profiler import null_rate
        value = null_rate(profile)
    elif key == "mean":
        from skim_csv.profiler import mean
        value = mean(profile)
    elif key == "min":
        value = profile.min_val
    elif key == "max":
        value = profile.max_val
    elif key == "unique":
        value = profile.unique_count
    else:
        raise ValueError(f"Unknown sort key '{key}'. Choose from: {_SORT_KEYS}")

    # Push None to the end regardless of direction
    if value is None:
        return (1, "") if not reverse else (0, "")
    return (0, value) if not reverse else (1, value)


def sort_profiles(
    profiles: List[ColumnProfile],
    key: str = "name",
    reverse: bool = False,
) -> List[ColumnProfile]:
    """Return *profiles* sorted by *key*.

    Parameters
    ----------
    profiles:
        List of :class:`ColumnProfile` instances to sort.
    key:
        Metric to sort by. One of ``name``, ``count``, ``null_rate``,
        ``mean``, ``min``, ``max``, ``unique``.
    reverse:
        If ``True``, sort in descending order.
    """
    if key not in _SORT_KEYS:
        raise ValueError(f"Unknown sort key '{key}'. Choose from: {_SORT_KEYS}")
    return sorted(
        profiles,
        key=lambda p: _profile_sort_key(p, key, reverse),
        reverse=reverse,
    )


def top_n(
    profiles: List[ColumnProfile],
    n: int,
    key: str = "null_rate",
) -> List[ColumnProfile]:
    """Return the top *n* profiles ranked by *key* (descending)."""
    ranked = sort_profiles(profiles, key=key, reverse=True)
    return ranked[:n]
