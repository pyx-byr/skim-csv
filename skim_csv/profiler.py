"""Column-level profiling logic for streaming CSV data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ColumnProfile:
    name: str
    count: int = 0
    null_count: int = 0
    numeric_count: int = 0
    min_value: float | None = None
    max_value: float | None = None
    _sum: float = field(default=0.0, repr=False)
    sample_values: list[str] = field(default_factory=list, repr=False)
    _sample_limit: int = field(default=5, repr=False)

    def update(self, raw_value: Any) -> None:
        self.count += 1
        value = str(raw_value).strip() if raw_value is not None else ""

        if value == "" or value.lower() in ("null", "none", "na", "n/a", "-"):
            self.null_count += 1
            return

        if len(self.sample_values) < self._sample_limit:
            self.sample_values.append(value)

        try:
            numeric = float(value)
            self.numeric_count += 1
            self._sum += numeric
            self.min_value = numeric if self.min_value is None else min(self.min_value, numeric)
            self.max_value = numeric if self.max_value is None else max(self.max_value, numeric)
        except ValueError:
            pass

    @property
    def null_rate(self) -> float:
        return self.null_count / self.count if self.count else 0.0

    @property
    def mean(self) -> float | None:
        return self._sum / self.numeric_count if self.numeric_count else None

    @property
    def is_numeric(self) -> bool:
        non_null = self.count - self.null_count
        return non_null > 0 and self.numeric_count == non_null


def profile_chunks(chunks: Any) -> dict[str, ColumnProfile]:
    """Build a profile dict from an iterable of row-chunk lists."""
    profiles: dict[str, ColumnProfile] = {}
    for chunk in chunks:
        for row in chunk:
            for col, value in row.items():
                if col not in profiles:
                    profiles[col] = ColumnProfile(name=col)
                profiles[col].update(value)
    return profiles
