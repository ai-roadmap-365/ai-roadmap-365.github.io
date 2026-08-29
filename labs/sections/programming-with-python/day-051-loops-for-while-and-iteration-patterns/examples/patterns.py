#!/usr/bin/env python3
"""Iteration Patterns Workbench — a complete, small, real program.

Demonstrates the five core loop patterns on a sequence of whole numbers:

    accumulate  — build a running total and count
    filter      — keep the items that pass a test
    transform   — make a new item from each old one
    search      — scan with an early break, and report the work done
    histogram   — build a small text histogram (counts of each value)

Numbers are read from standard input (whitespace-separated), except the
`demo` command, which uses a built-in sample list so it needs no input.

Usage:
    python3 patterns.py demo                     # show all five patterns
    echo "3 1 4 1 5 9 2 6" | python3 patterns.py total
    echo "3 1 4 1 5 9 2 6" | python3 patterns.py filter 4
    echo "3 1 4 1 5 9 2 6" | python3 patterns.py transform
    echo "3 1 4 1 5 9 2 6" | python3 patterns.py search 5
    echo "1 2 2 3 3 3"     | python3 patterns.py histogram

Bad input (a non-number token, an unknown command, or a missing argument)
prints a clear error to standard error and exits with a non-zero code.
"""
import sys

SAMPLE = [3, 1, 4, 1, 5, 9, 2, 6]


def read_numbers(text):
    """Parse whitespace-separated whole numbers from text into a list of int.

    Raises ValueError naming the first token that is not a whole number.
    """
    numbers = []
    for token in text.split():
        try:
            numbers.append(int(token))
        except ValueError:
            raise ValueError(f"'{token}' is not a whole number")
    return numbers


def accumulate_total(numbers):
    """Accumulator pattern: return (count, total) built one item per pass."""
    count = 0
    total = 0
    for n in numbers:
        count = count + 1
        total = total + n
    return count, total


def filter_above(numbers, threshold):
    """Filter pattern: return the items strictly greater than threshold."""
    kept = []
    for n in numbers:
        if n > threshold:
            kept.append(n)
    return kept


def transform_squares(numbers):
    """Transform pattern: return a new list with each item squared."""
    squares = []
    for n in numbers:
        squares.append(n * n)
    return squares


def linear_search(numbers, target):
    """Search pattern with early break.

    Return (index, comparisons): index is the position of the first item
    equal to target, or -1 if absent; comparisons is how many items were
    inspected — fewer when the target is found early, thanks to break.
    """
    comparisons = 0
    for index, n in enumerate(numbers):
        comparisons = comparisons + 1
        if n == target:
            return index, comparisons
    return -1, comparisons


def build_histogram(numbers):
    """Build a text histogram: for each distinct value, a bar of '#' per count.

    Returns a list of aligned label-and-bar strings, sorted by value.
    """
    counts = {}
    for n in numbers:
        counts[n] = counts.get(n, 0) + 1
    if not counts:
        return []
    width = max(len(str(value)) for value in counts)
    rows = []
    for value in sorted(counts):
        bar = ""
        for _ in range(counts[value]):
            bar = bar + "#"
        rows.append(f"{str(value).rjust(width)} | {bar}")
    return rows


def run_command(command, args, numbers):
    """Dispatch one command. Returns (lines_to_print, exit_code)."""
    if command == "total":
        count, total = accumulate_total(numbers)
        return [f"count={count} sum={total}"], 0

    if command == "filter":
        if len(args) != 1:
            raise ValueError("filter needs one threshold, e.g. filter 4")
        threshold = int_arg(args[0], "threshold")
        return [str(filter_above(numbers, threshold))], 0

    if command == "transform":
        return [str(transform_squares(numbers))], 0

    if command == "search":
        if len(args) != 1:
            raise ValueError("search needs one target, e.g. search 5")
        target = int_arg(args[0], "target")
        index, comparisons = linear_search(numbers, target)
        if index == -1:
            return [f"{target} not found after {comparisons} comparisons"], 1
        return [f"found {target} at index {index} after {comparisons} comparisons"], 0

    if command == "histogram":
        return build_histogram(numbers), 0

    raise ValueError(f"unknown command '{command}'")


def int_arg(text, name):
    """Parse a command argument to int, raising a clear ValueError on failure."""
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"{name} must be a whole number, not '{text}'")


def demo():
    """Run every pattern on the built-in SAMPLE list; needs no input."""
    numbers = SAMPLE
    count, total = accumulate_total(numbers)
    lines = [
        f"sample: {numbers}",
        f"total    -> count={count} sum={total}",
        f"filter>4 -> {filter_above(numbers, 4)}",
        f"transform-> {transform_squares(numbers)}",
    ]
    index, comparisons = linear_search(numbers, 5)
    lines.append(
        f"search 5 -> found 5 at index {index} after {comparisons} comparisons"
    )
    lines.append("histogram:")
    lines.extend(build_histogram(numbers))
    return lines


def main(argv):
    """Entry point. Returns an exit code: 0 on success, non-zero on error."""
    if len(argv) < 2:
        print("error: no command given", file=sys.stderr)
        print(usage(), file=sys.stderr)
        return 1

    command = argv[1]
    args = argv[2:]

    if command in ("-h", "--help", "help"):
        print(usage())
        return 0

    if command == "demo":
        for line in demo():
            print(line)
        return 0

    try:
        numbers = read_numbers(sys.stdin.read())
        lines, code = run_command(command, args, numbers)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        print(usage(), file=sys.stderr)
        return 1

    for line in lines:
        print(line)
    return code


def usage():
    """Return the one-block usage string."""
    return (
        "usage: python3 patterns.py <command> [arg]\n"
        "  commands (read numbers from stdin, except demo):\n"
        "    demo                 show all five patterns on a sample list\n"
        "    total                accumulate: print count and sum\n"
        "    filter <threshold>   keep items greater than threshold\n"
        "    transform            square each item\n"
        "    search <target>      find target with an early break\n"
        "    histogram            counts of each value as '#' bars"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
