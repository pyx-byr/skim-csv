"""Command-line interface for skim-csv."""

from __future__ import annotations

import argparse
import sys
from typing import List

from skim_csv.reader import stream_csv, iter_rows, detect_headers
from skim_csv.profiler import ColumnProfile, update
from skim_csv.formatter import render_table
from skim_csv.exporter import export_profiles


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skim-csv",
        description="Fast CSV profiler — summarise large files without loading them fully.",
    )
    parser.add_argument("file", help="Path to the CSV file to profile.")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1024 * 64,
        metavar="BYTES",
        help="Read chunk size in bytes (default: 65536).",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        metavar="CHAR",
        help="CSV delimiter character (default: comma).",
    )
    parser.add_argument(
        "--export",
        choices=["json", "csv"],
        default=None,
        metavar="FORMAT",
        help="Export profile summary as 'json' or 'csv' instead of table.",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write export output to FILE instead of stdout.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        chunks = stream_csv(args.file, chunk_size=args.chunk_size)
        headers, rows = iter_rows(chunks, delimiter=args.delimiter)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    profiles: List[ColumnProfile] = [ColumnProfile(name=h) for h in headers]

    for row in rows:
        for profile, value in zip(profiles, row):
            update(profile, value)

    if args.export:
        output = export_profiles(profiles, args.export)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(output)
            print(f"Profile exported to {args.output}")
        else:
            print(output)
    else:
        print(render_table(profiles))

    return 0


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":  # pragma: no cover
    main()
