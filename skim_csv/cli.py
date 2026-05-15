"""Command-line interface for skim-csv."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from skim_csv.pipeline import profile_file, summarise
from skim_csv.formatter import render_table
from skim_csv.exporter import export_profiles
from skim_csv.sorter import sort_profiles, top_n, _SORT_KEYS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skim-csv",
        description="Fast CSV profiler — summarise large files without loading them fully.",
    )
    parser.add_argument("file", help="Path to the CSV file to profile.")
    parser.add_argument(
        "--delimiter", "-d", default=",", help="Field delimiter (default: comma)."
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Treat the first row as data, not a header.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        metavar="N",
        help="Rows per read chunk (default: 1000).",
    )
    parser.add_argument(
        "--output", "-o",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table).",
    )
    parser.add_argument(
        "--sort-by",
        choices=list(_SORT_KEYS),
        default="name",
        metavar="KEY",
        help=f"Sort columns by metric. Choices: {_SORT_KEYS} (default: name).",
    )
    parser.add_argument(
        "--sort-desc",
        action="store_true",
        help="Sort in descending order.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="Show only the top N columns after sorting.",
    )
    parser.add_argument(
        "--filter",
        dest="filters",
        action="append",
        metavar="COL:OP:VAL",
        help="Row filter expression, e.g. age:gt:30. May be repeated.",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        profiles = profile_file(
            args.file,
            delimiter=args.delimiter,
            has_header=not args.no_header,
            chunk_size=args.chunk_size,
            filter_exprs=args.filters or [],
        )
    except FileNotFoundError as exc:
        print(f"skim-csv: error: {exc}", file=sys.stderr)
        return 1

    # Sort
    profiles = sort_profiles(profiles, key=args.sort_by, reverse=args.sort_desc)

    # Limit
    if args.top is not None:
        profiles = profiles[: args.top]

    if args.output == "table":
        print(render_table(profiles))
    else:
        print(export_profiles(profiles, fmt=args.output))

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())
