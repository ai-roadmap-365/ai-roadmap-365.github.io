"""The command-line half of ``wordtally-tools``.

``[project.scripts]`` in ``pyproject.toml`` points at :func:`main` here. When
the package is installed, the installer writes a small executable named
``wordtally`` into the environment's ``bin/`` directory whose entire body is
"import this function and ``sys.exit()`` its return value". That is why
:func:`main` returns an ``int`` rather than calling ``sys.exit`` itself: a
function that returns is testable, and Day 80 made that the habit.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from wordtally import __version__
from wordtally.core import count_words, top_words

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser. Separate from :func:`main` so tests can
    inspect the parser without running anything."""
    parser = argparse.ArgumentParser(
        prog="wordtally",
        description="Count and rank the words in a text file.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"wordtally {__version__}",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    count = subcommands.add_parser("count", help="print the number of words")
    count.add_argument("path", help="file to read, or - for standard input")

    top = subcommands.add_parser("top", help="print the most frequent words")
    top.add_argument("path", help="file to read, or - for standard input")
    top.add_argument(
        "-n",
        type=int,
        default=3,
        help="how many words to print (default: 3)",
    )
    top.add_argument(
        "--keep-stopwords",
        action="store_true",
        help="do not filter out common words such as the and and",
    )
    return parser


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = _read(args.path)
    except OSError as error:
        print(f"wordtally: cannot read {args.path}: {error}", file=sys.stderr)
        return 2

    if args.command == "count":
        print(count_words(text))
        return 0

    try:
        ranked = top_words(text, args.n, skip_stopwords=not args.keep_stopwords)
    except ValueError as error:
        print(f"wordtally: {error}", file=sys.stderr)
        return 2
    for word, count in ranked:
        print(f"{count:>6}  {word}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
