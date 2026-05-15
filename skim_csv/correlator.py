"""Compute pairwise Pearson correlations between numeric columns."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .profiler import ColumnProfile


@dataclass
class ColumnCorrelation:
    col_a: str
    col_b: str
    r: float  # Pearson r, or None if undefined
    n: int    # number of paired observations

    def __repr__(self) -> str:  # pragma: no cover
        return f"ColumnCorrelation({self.col_a!r}, {self.col_b!r}, r={self.r:.4f}, n={self.n})"


def _pearson(
    pairs: List[Tuple[float, float]]
) -> Tuple[float | None, int]:
    """Return (r, n) for a list of (x, y) float pairs."""
    n = len(pairs)
    if n < 2:
        return None, n
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if std_x == 0 or std_y == 0:
        return None, n
    return cov / (std_x * std_y), n


def correlate_columns(
    rows: List[Dict[str, str]],
    profiles: List[ColumnProfile],
) -> List[ColumnCorrelation]:
    """Return pairwise Pearson correlations for all numeric column pairs."""
    numeric_cols = [p.name for p in profiles if p.is_numeric]
    results: List[ColumnCorrelation] = []

    for i, col_a in enumerate(numeric_cols):
        for col_b in numeric_cols[i + 1:]:
            pairs: List[Tuple[float, float]] = []
            for row in rows:
                try:
                    x = float(row[col_a])
                    y = float(row[col_b])
                    pairs.append((x, y))
                except (ValueError, KeyError):
                    pass
            r, n = _pearson(pairs)
            if r is not None:
                results.append(ColumnCorrelation(col_a, col_b, r, n))

    return results


def top_correlations(
    correlations: List[ColumnCorrelation],
    n: int = 10,
    absolute: bool = True,
) -> List[ColumnCorrelation]:
    """Return the top-n correlations sorted by |r| descending."""
    key = (lambda c: abs(c.r)) if absolute else (lambda c: c.r)
    return sorted(correlations, key=key, reverse=True)[:n]
