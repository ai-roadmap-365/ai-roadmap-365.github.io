#!/usr/bin/env python3
"""summary.py — the imperative shell of the summary tool.

This is the ONLY part of the program that touches the outside world. It
reads command-line arguments, opens a file or reads standard input, prints
the result to standard output, prints errors to standard error, and chooses
the exit code. It contains no statistics logic of its own: it calls the
pure functions in summary_core.py and arranges their inputs and outputs.

Because all the messiness lives here and all the logic lives in the core,
the core can be tested with plain function calls while this thin shell just
wires it to the world.

Usage:
    python3 summary.py numbers.txt          # read from a file
    echo "1 2 3 4 5" | python3 summary.py   # read from standard input
"""
import sys

import summary_core


def read_input(argv):
    """Return the raw text to summarize: from a named file, or from stdin.

    This lives in the shell, not the core, because it performs I/O. It is
    the one place in the program that knows where the bytes come from.
    """
    if len(argv) > 1:
        with open(argv[1], "r", encoding="utf-8") as handle:
            return handle.read()
    return sys.stdin.read()


def main(argv):
    """Wire the shell to the core: read input, run the core, print, exit.

    Any error the core raises (bad token, empty input) or the filesystem
    raises (missing file) becomes a clear message on standard error and a
    non-zero exit code, so a script calling this tool can detect failure.
    """
    try:
        text = read_input(argv)
        numbers = summary_core.parse_numbers(text)
        summary = summary_core.summarize(numbers)
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    print(summary_core.format_summary(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
