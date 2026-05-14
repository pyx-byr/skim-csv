"""Row sampling utilities for skim-csv.

Provides reservoir sampling to extract a representative sample
from a CSV stream without loading the full file into memory.
"""

from __future__ import annotations

import random
from typing import Iterator, List

from skim_csv.reader import iter_rows


def reservoir_sample(
    filepath: str,
    n: int = 100,
    has_header: bool = True,
    seed: int | None = None,
) -> tuple[list[str], list[list[str]]]:
    """Return up to *n* rows sampled uniformly from the CSV file.

    Uses Vitter's reservoir sampling algorithm (Algorithm R) so the
    entire file is never held in memory.

    Parameters
    ----------
    filepath:
        Path to the CSV file.
    n:
        Desired sample size (fewer rows returned if file is smaller).
    has_header:
        When ``True`` the first row is treated as a header and returned
        separately; it is never included in the sample.
    seed:
        Optional RNG seed for reproducibility.

    Returns
    -------
    headers:
        List of column names (empty list when *has_header* is ``False``).
    sample:
        List of sampled rows, each row being a list of string values.
    """
    rng = random.Random(seed)
    reservoir: list[list[str]] = []
    headers: list[str] = []

    row_iter: Iterator[list[str]] = iter_rows(filepath)

    if has_header:
        try:
            headers = next(row_iter)
        except StopIteration:
            return [], []

    for index, row in enumerate(row_iter):
        if index < n:
            reservoir.append(row)
        else:
            swap_pos = rng.randint(0, index)
            if swap_pos < n:
                reservoir[swap_pos] = row

    return headers, reservoir


def sample_to_dicts(
    headers: list[str], sample: list[list[str]]
) -> list[dict[str, str]]:
    """Zip *headers* with each row in *sample* to produce a list of dicts."""
    if not headers:
        return [{str(i): v for i, v in enumerate(row)} for row in sample]
    return [dict(zip(headers, row)) for row in sample]
