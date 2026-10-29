"""Command-line interface for CodeShape."""

import argparse
import os
from pathlib import Path
import sys

from codeshape import __version__
from codeshape.analyzer import analyze_codebase
from codeshape.formatter import format_json, format_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codeshape",
        description="Analyze codebase file-size distribution and Code Shape Score.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to analyze (default: current directory)",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=100,
        help="Line count threshold per file (default: 100)",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Additional ignore pattern, repeatable (e.g. -i 'tests/' -i '*.gen.py')",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=None,
        help="Number of largest files to list (default: 20, 0 for all)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output analysis as JSON",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI terminal colors",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    target = Path(args.path)

    if not target.exists():
        print(f"Error: path '{args.path}' does not exist.", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"Error: path '{args.path}' is not a directory.", file=sys.stderr)
        return 1
    if args.threshold < 1:
        print("Error: --threshold must be >= 1.", file=sys.stderr)
        return 1

    result = analyze_codebase(
        target=target,
        threshold=args.threshold,
        extra_ignores=args.ignore,
    )

    if args.json:
        print(format_json(result, top=args.top))
        return 0

    use_color = (
        not args.no_color
        and sys.stdout.isatty()
        and os.environ.get("NO_COLOR") is None
    )
    top = 20 if args.top is None else max(0, args.top)
    print(format_report(result, top=top, use_color=use_color))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
