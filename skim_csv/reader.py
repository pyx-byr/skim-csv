"""Streaming CSV reader that processes files in chunks without loading fully into memory."""

import csv
from pathlib import Path
from typing import Generator, Iterator

DEFAULT_CHUNK_SIZE = 1000


def stream_csv(
    filepath: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    encoding: str = "utf-8",
    delimiter: str = ",",
) -> Generator[list[dict], None, None]:
    """Yield chunks of rows from a CSV file as lists of dicts.

    Args:
        filepath: Path to the CSV file.
        chunk_size: Number of rows per chunk.
        encoding: File encoding.
        delimiter: CSV delimiter character.

    Yields:
        A list of dicts representing a chunk of rows.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    if filepath.stat().st_size == 0:
        raise ValueError(f"CSV file is empty: {filepath}")

    with filepath.open(encoding=encoding, newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        chunk: list[dict] = []
        for row in reader:
            chunk.append(dict(row))
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


def iter_rows(
    filepath: str | Path,
    encoding: str = "utf-8",
    delimiter: str = ",",
) -> Iterator[dict]:
    """Iterate over every row in a CSV file one at a time.

    Args:
        filepath: Path to the CSV file.
        encoding: File encoding.
        delimiter: CSV delimiter character.

    Yields:
        A single row as a dict.
    """
    for chunk in stream_csv(filepath, chunk_size=DEFAULT_CHUNK_SIZE,
                            encoding=encoding, delimiter=delimiter):
        yield from chunk


def detect_headers(filepath: str | Path, encoding: str = "utf-8",
                   delimiter: str = ",") -> list[str]:
    """Return the header column names from a CSV file."""
    filepath = Path(filepath)
    with filepath.open(encoding=encoding, newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        return list(reader.fieldnames or [])
