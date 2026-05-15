"""CLI entry-point for diffing two CSV files."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from skim_csv.pipeline import profile_file
from skim_csv.differ import diff_profiles
from skim_csv.diff_formatter import render_diff_table


def build_diff_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skim-diff",
        description="Compare column profiles of two CSV files.",
    )
    parser.add_argument("left", help="First (baseline) CSV file")
    parser.add_argument("right", help="Second CSV file to compare against")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        metavar="N",
        help="Rows per chunk (default: 1000)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8)",
    )
    return parser


def run_diff(argv: Optional[List[str]] = None) -> int:
    """Parse arguments, compute diff, print table. Returns exit code."""
    parser = build_diff_parser()
    args = parser.parse_args(argv)

    try:
        left_profiles = profile_file(
            args.left,
            chunk_size=args.chunk_size,
            encoding=args.encoding,
        )
        right_profiles = profile_file(
            args.right,
            chunk_size=args.chunk_size,
            encoding=args.encoding,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    diffs = diff_profiles(left_profiles, right_profiles)
    print(render_diff_table(diffs))
    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run_diff())


if __name__ == "__main__":  # pragma: no cover
    main()
