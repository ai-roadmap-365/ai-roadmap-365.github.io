#!/usr/bin/env python3
"""by_hand.py — what parsing sys.argv yourself actually costs.

Day 56 built a data-driven command-line tool with sys.argv, and for one
positional argument that is the right call: argparse would have been more
machinery than the job needed. This file shows the exact point where that
stops being true.

Run it with no arguments to watch a hand-rolled parser be put through eight
ordinary command lines, four of which it gets wrong. Nothing here is a straw
man: this is the shape people really write, right down to the manual index
arithmetic.

    python3 by_hand.py

The point is not that hand-parsing is impossible. It is that everything the
hand-rolled version is missing — help text, a usage message, exit code 2,
short and long forms, `--flag=value`, clustered short flags, `--` to end
option parsing, type conversion, and the promise that an unknown option is
refused rather than ignored — is a line of argparse each.
"""

from __future__ import annotations

import sys


def parse_by_hand(argv: list[str]) -> dict[str, object]:
    """A hand-rolled parser for: notes add TEXT [--tag T] [--dry-run].

    Written the way a hand-rolled parser is usually written: walk the list,
    branch on what you find, and hope.
    """
    text: str | None = None
    tag: str | None = None
    dry_run = False

    i = 0
    while i < len(argv):
        item = argv[i]
        if item == "--dry-run":
            dry_run = True
        elif item == "--tag":
            i += 1
            tag = argv[i]  # IndexError if the user forgot the value
        elif text is None:
            text = item
        i += 1

    return {"text": text, "tag": tag, "dry_run": dry_run}


# Each case is (argv, correct?, comment). The `correct?` flag is stated
# explicitly rather than guessed from the text, because a count that depends
# on string-matching its own commentary is exactly the kind of quiet wrongness
# this file is about.
CASES: list[tuple[list[str], bool, str]] = [
    (["buy milk"], True, "the happy path — this one works"),
    (["buy milk", "--tag", "shopping"], True, "an option with a value — also fine"),
    (["buy milk", "--tag", "shopping", "--dry-run"], True, "two options — still fine"),
    (["buy milk", "--tag=shopping"], False, "--flag=value form: the tag is silently lost"),
    (["buy milk", "-t", "shopping"], False, "short form: -t is swallowed as the text"),
    (["buy milk", "--drynrun"], False, "a typo: accepted in silence, and does nothing"),
    (["--dry-run", "buy milk"], True, "options before the text — right answer, by luck"),
    (["buy milk", "--tag"], False, "a missing value: IndexError, and a traceback"),
]


def main() -> int:
    print("A hand-rolled parser for: notes add TEXT [--tag T] [--dry-run]")
    print()
    wrong = 0
    for argv, correct, comment in CASES:
        printable = " ".join(repr(a) if " " in a else a for a in argv)
        try:
            result = parse_by_hand(argv)
            got = f"text={result['text']!r} tag={result['tag']!r} dry_run={result['dry_run']}"
        except IndexError:
            got = "IndexError: list index out of range"
        print(f"  $ notes add {printable}")
        print(f"      {got}")
        print(f"      {comment}")
        print()
        if not correct:
            wrong += 1

    print(f"{len(CASES)} ordinary command lines, {wrong} of them handled wrongly.")
    print()
    print("None of these is exotic. Every one of them is something a user")
    print("types on their first afternoon with your tool. And this parser")
    print("still has no --help, no usage message, no exit code 2, no type")
    print("conversion, and no way to refuse an option it does not know.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
