"""__main__.py — the package's entry point: ``python3 -m wordstats FILE``.

Runs when you execute ``python3 -m wordstats``. It reads a file (or standard
input), asks the sibling modules to do their jobs, and prints a report. The
imports below are RELATIVE (the leading dot means "this same package").
"""
import sys

from .tokens import tokenize
from .stats import top_n


def report(text, n=5):
    """Return the printable top-n report for a block of text (no input/output)."""
    # Exercise 4: THE REPORT (pure: text in, string out — no printing here).
    # 1. words = tokenize(text)
    # 2. Start a list of lines with:
    #        f"{len(words)} words, {len(set(words))} unique"
    # 3. For each (word, count) in top_n(words, n), numbered from 1, append:
    #        f"{rank}. {word}: {count}"
    #    Hint: enumerate(top_n(words, n), start=1) gives (rank, (word, count)).
    # 4. Return "\n".join(lines).
    raise NotImplementedError("Exercise 4: implement report")


def main(argv):
    """Read the file named on the command line (or stdin), print the report."""
    if len(argv) > 1:
        with open(argv[1], "r", encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.read()
    print(report(text))
    return 0


# Exercise 6: ADD THE MAIN GUARD.
# Below this comment, add the guard so that running the package executes main
# but importing this module (for example to test report) does not:
#
#     if __name__ == "__main__":
#         sys.exit(main(sys.argv))
