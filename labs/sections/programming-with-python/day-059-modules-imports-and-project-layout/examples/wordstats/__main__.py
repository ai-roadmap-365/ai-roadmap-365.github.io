"""__main__.py — the package's entry point: ``python3 -m wordstats FILE``.

Because this file is named ``__main__.py``, running ``python3 -m wordstats``
executes it. It reads a text file (or standard input when no file is given),
asks ``tokens`` and ``stats`` to do their jobs, and prints a small report.

The ``if __name__ == "__main__":`` guard at the very bottom is what lets this
same file be *imported* (to reuse ``report`` in a test) as well as *run* (as a
program): the guarded code runs only when the file is executed directly, not
when another module imports it.
"""
import sys

from .tokens import tokenize
from .stats import top_n


def report(text, n=5):
    """Return the printable top-n report for a block of text (no input/output).

    Keeping this pure — text in, string out, nothing read or printed — is what
    makes it importable and testable without a file or a terminal.
    """
    words = tokenize(text)
    lines = [f"{len(words)} words, {len(set(words))} unique"]
    for rank, (word, count) in enumerate(top_n(words, n), start=1):
        lines.append(f"{rank}. {word}: {count}")
    return "\n".join(lines)


def main(argv):
    """Read the file named on the command line (or stdin), print the report."""
    if len(argv) > 1:
        with open(argv[1], "r", encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.read()
    print(report(text))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
