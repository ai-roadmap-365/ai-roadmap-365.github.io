#!/usr/bin/env python3
"""Day 047 lab — a friendly CLI greeter/calculator (reference solution).

Reads two numbers EITHER from a command-line argument OR from standard input,
so it is testable non-interactively:

    python3 io_demo.py 5 7
    echo "5 7" | python3 io_demo.py

It converts the input safely (a clear error on bad input), computes a small
stats line, and prints a nicely f-string-formatted, aligned report. On bad
input it writes a message to STANDARD ERROR and exits with a non-zero code, so
the failure is visible to a shell or a calling script.
"""
import sys


def read_raw() -> str:
    """Return the raw input text: the command-line argument if given,
    otherwise everything piped in on standard input."""
    if len(sys.argv) > 1:
        # Join all positional args so both `io_demo.py 5 7` and
        # `io_demo.py "5 7"` work.
        return " ".join(sys.argv[1:])
    return sys.stdin.read()


def parse_pair(raw: str) -> tuple[float, float]:
    """Split the raw text into exactly two numbers, converting safely.

    Raises ValueError with a clear message if there are not exactly two
    whitespace-separated tokens or if either token is not a number.
    """
    parts = raw.split()
    if len(parts) != 2:
        raise ValueError(f"expected two numbers, got {len(parts)}")
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        # Re-raise with the original text so the message is actionable.
        raise ValueError(f"both inputs must be numbers (got {raw.strip()!r})")


def format_report(a: float, b: float) -> str:
    """Build the aligned, f-string-formatted report as one string."""
    total = a + b
    product = a * b
    mean = total / 2
    lines = [
        "Input values",
        f"  {'a':<9}{a:>8.2f}",
        f"  {'b':<9}{b:>8.2f}",
        "Results",
        f"  {'sum':<9}{total:>8.2f}",
        f"  {'product':<9}{product:>8.2f}",
        f"  {'mean':<9}{mean:>8.2f}",
    ]
    return "\n".join(lines)


def main() -> int:
    raw = read_raw()
    try:
        a, b = parse_pair(raw)
    except ValueError as err:
        # Diagnostics go to STDERR, never stdout, so a pipeline stays clean.
        print(f"error: {err}", file=sys.stderr)
        return 1
    print(format_report(a, b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
