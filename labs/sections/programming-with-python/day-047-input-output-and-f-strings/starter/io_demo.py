#!/usr/bin/env python3
"""Day 047 lab starter — complete the five numbered exercises below.

Goal: read two numbers (from a command-line argument OR from standard input),
convert them safely, and print an aligned, f-string-formatted report. On bad
input, write an error to STANDARD ERROR and exit with a non-zero code.

See the finished target first:
    python3 examples/io_demo.py 5 7
    echo "5 7" | python3 examples/io_demo.py

Then complete each exercise, replacing every "FILL_ME_IN", and run:
    bash tests/run_tests.sh

The sentinel FILL_ME_IN below is how the test knows the lab is unfinished.
"""
import sys

FILL_ME_IN = "FILL_ME_IN"


def read_raw() -> str:
    """Exercise 1 — read the input from EITHER the command line OR stdin.

    If arguments were given (len(sys.argv) > 1), join sys.argv[1:] with a
    single space and return that string. Otherwise, return sys.stdin.read().
    Reading both ways is what makes the program testable without a keyboard.
    Replace the return below with that logic.
    """
    return FILL_ME_IN


def parse_pair(raw: str) -> tuple[float, float]:
    """Exercises 2 and 4 — turn the raw text into exactly two numbers, safely.

    Exercise 2 (convert): split raw into tokens with raw.split(); if there are
      not exactly two tokens, raise ValueError(f"expected two numbers, got
      {len(parts)}").
    Exercise 4 (handle bad input): convert with float(parts[0]) and
      float(parts[1]) inside a try/except ValueError, and in the except branch
      raise ValueError(f"both inputs must be numbers (got {raw.strip()!r})").
    Remember: input text is a str — float() is what makes it a number.
    """
    parts = raw.split()
    # ... your Exercise 2 length check goes here ...
    # ... your Exercise 4 try/except conversion goes here ...
    return float(parts[0]), float(parts[1])  # replace with the safe version


def format_report(a: float, b: float) -> str:
    """Exercise 3 — format each value right-aligned to width 8, two decimals.

    Each value below currently prints with no formatting. Give every number an
    f-string spec of the form {value:>8.2f} so the two columns line up and show
    exactly two decimal places (compare against examples/io_demo.py).
    """
    total = a + b
    product = a * b
    mean = total / 2
    lines = [
        "Input values",
        f"  {'a':<9}{a}",          # replace {a} with {a:>8.2f}
        f"  {'b':<9}{b}",          # replace {b} with {b:>8.2f}
        "Results",
        f"  {'sum':<9}{total}",    # replace {total} with the aligned spec
        f"  {'product':<9}{product}",
        f"  {'mean':<9}{mean}",
    ]
    return "\n".join(lines)


def main() -> int:
    raw = read_raw()
    try:
        a, b = parse_pair(raw)
    except ValueError as err:
        # Exercise 5 — write the error to STANDARD ERROR (not stdout) so it
        # never pollutes a pipeline, then signal failure with a non-zero code.
        # Add  file=sys.stderr  to the print below.
        print(f"error: {err}")  # <- add file=sys.stderr
        return 1
    print(format_report(a, b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
