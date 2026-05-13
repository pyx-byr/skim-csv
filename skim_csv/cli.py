"""Command-line entry point for skim-csv."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skim_csv.formatter import render_table
from skim_csv.profiler import profile_chunks
from skim_csv.reader import stream_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skim-csv",
        description="Fast CSV profiler — no full load into memory.",
    )
    parser.add_argument("file", type=Path, help="Path to the CSV file.")
    parser.add_argument(
        "--chunk-size", type=int, default=1000,
        metavar="N", help="Rows per processing chunk (default: 1000)."
    )
    parser.add_argument(
        "--delimiter", default=",",
        help="CSV delimiter character (default: comma)."
    )
    parser.add_argument(
        "--encoding", default="utf-8",
        help="File encoding (default: utf-8)."
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        chunks = stream_csv(
            args.file,
            chunk_size=args.chunk_size,
            encoding=args.encoding,
            delimiter=args.delimiter,
        )
        profiles = profile_chunks(chunks)
        total_rows = next(iter(profiles.values())).count if profiles else 0
        print(render_table(profiles, total_rows))
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
