"""Compare column profiles between two CSV files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from skim_csv.profiler import ColumnProfile


@dataclass
class ColumnDiff:
    """Difference summary for a single column."""

    name: str
    in_left: bool
    in_right: bool
    row_count_left: Optional[int] = None
    row_count_right: Optional[int] = None
    null_rate_left: Optional[float] = None
    null_rate_right: Optional[float] = None
    mean_left: Optional[float] = None
    mean_right: Optional[float] = None

    @property
    def only_in_left(self) -> bool:
        return self.in_left and not self.in_right

    @property
    def only_in_right(self) -> bool:
        return self.in_right and not self.in_left

    @property
    def null_rate_delta(self) -> Optional[float]:
        if self.null_rate_left is not None and self.null_rate_right is not None:
            return self.null_rate_right - self.null_rate_left
        return None

    @property
    def mean_delta(self) -> Optional[float]:
        if self.mean_left is not None and self.mean_right is not None:
            return self.mean_right - self.mean_left
        return None


def diff_profiles(
    left: Dict[str, ColumnProfile],
    right: Dict[str, ColumnProfile],
) -> List[ColumnDiff]:
    """Return a list of ColumnDiff objects comparing two sets of profiles."""
    all_names = sorted(set(left) | set(right))
    diffs: List[ColumnDiff] = []

    for name in all_names:
        lp = left.get(name)
        rp = right.get(name)

        from skim_csv.profiler import null_rate, mean as profile_mean

        diffs.append(
            ColumnDiff(
                name=name,
                in_left=lp is not None,
                in_right=rp is not None,
                row_count_left=lp.count if lp else None,
                row_count_right=rp.count if rp else None,
                null_rate_left=null_rate(lp) if lp else None,
                null_rate_right=null_rate(rp) if rp else None,
                mean_left=profile_mean(lp) if lp else None,
                mean_right=profile_mean(rp) if rp else None,
            )
        )

    return diffs
