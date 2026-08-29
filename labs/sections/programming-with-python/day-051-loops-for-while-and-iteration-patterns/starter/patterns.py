#!/usr/bin/env python3
"""Iteration Patterns Workbench — YOUR working file.

Complete the five numbered exercises below, one per loop pattern. Each stub
raises NotImplementedError until you finish it. The finished reference is in
examples/patterns.py — try each exercise yourself before peeking.

When all five are done, this file behaves just like the reference:

    python3 starter/patterns.py demo
    echo "3 1 4 1 5 9 2 6" | python3 starter/patterns.py total   -> count=8 sum=31

Then run:  bash tests/run_tests.sh
"""
import sys

SAMPLE = [3, 1, 4, 1, 5, 9, 2, 6]


def read_numbers(text):
    """Parse whitespace-separated whole numbers into a list of int.

    Raises ValueError naming the first token that is not a whole number.
    (Provided — study how the loop validates each token at the boundary.)
    """
    numbers = []
    for token in text.split():
        try:
            numbers.append(int(token))
        except ValueError:
            raise ValueError(f"'{token}' is not a whole number")
    return numbers


def accumulate_total(numbers):
    """Accumulator pattern: return (count, total)."""
    # Exercise 1: ACCUMULATE.
    # Start count and total at 0 (the neutral values). Loop over `numbers`
    # with a for loop; each pass, add 1 to count and add the item to total.
    # Return (count, total). Verify by hand: [3,1,4,1,5,9,2,6] -> (8, 31).
    raise NotImplementedError("Exercise 1: implement accumulate_total")


def filter_above(numbers, threshold):
    """Filter pattern: return the items strictly greater than threshold."""
    # Exercise 2: FILTER.
    # Start with an empty list `kept`. Loop over `numbers`; if an item is
    # greater than `threshold`, append it to `kept`. Return `kept`.
    # Example: filter_above([3,1,4,1,5,9,2,6], 4) -> [5, 9, 6].
    raise NotImplementedError("Exercise 2: implement filter_above")


def transform_squares(numbers):
    """Transform pattern: return a new list with each item squared."""
    # Exercise 3: TRANSFORM.
    # Start with an empty list. Loop over `numbers`; append n * n for each n.
    # Example: transform_squares([3,1,4]) -> [9, 1, 16].
    raise NotImplementedError("Exercise 3: implement transform_squares")


def linear_search(numbers, target):
    """Search pattern with early break.

    Return (index, comparisons): index of the first item equal to target,
    or -1 if absent; comparisons is how many items were inspected.
    """
    # Exercise 4: SEARCH WITH EARLY BREAK.
    # Count comparisons starting at 0. Loop with enumerate(numbers); each
    # pass, add 1 to comparisons. As soon as an item equals `target`, RETURN
    # (index, comparisons) immediately (this is the early exit — do not keep
    # scanning). If the loop finishes without a match, return (-1, comparisons).
    raise NotImplementedError("Exercise 4: implement linear_search")


def build_histogram(numbers):
    """Build a text histogram: for each distinct value, a bar of '#' per count."""
    # Exercise 5: HISTOGRAM (accumulate counts, then build bars).
    # 1. Build a dict `counts` mapping each value to how many times it appears
    #    (loop over numbers; counts[n] = counts.get(n, 0) + 1).
    # 2. If counts is empty, return [].
    # 3. Let width = the length of the widest value's text (for alignment).
    # 4. For each value in sorted(counts), build a bar of counts[value] '#'
    #    characters and append f"{str(value).rjust(width)} | {bar}" to a list.
    # Return the list. Example on [1,2,2,3,3,3]: ['1 | #', '2 | ##', '3 | ###'].
    raise NotImplementedError("Exercise 5: implement build_histogram")


# ---------------------------------------------------------------------------
# Everything below is provided: command dispatch, main, and usage. Once the
# five functions above work, the whole program runs like the reference.
# ---------------------------------------------------------------------------


def int_arg(text, name):
    """Parse a command argument to int, raising a clear ValueError on failure."""
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"{name} must be a whole number, not '{text}'")


def run_command(command, args, numbers):
    """Dispatch one command. Returns (lines_to_print, exit_code)."""
    if command == "total":
        count, total = accumulate_total(numbers)
        return [f"count={count} sum={total}"], 0
    if command == "filter":
        if len(args) != 1:
            raise ValueError("filter needs one threshold, e.g. filter 4")
        return [str(filter_above(numbers, int_arg(args[0], "threshold")))], 0
    if command == "transform":
        return [str(transform_squares(numbers))], 0
    if command == "search":
        if len(args) != 1:
            raise ValueError("search needs one target, e.g. search 5")
        index, comparisons = linear_search(numbers, int_arg(args[0], "target"))
        if index == -1:
            return [f"{args[0]} not found after {comparisons} comparisons"], 1
        return [f"found {args[0]} at index {index} after {comparisons} comparisons"], 0
    if command == "histogram":
        return build_histogram(numbers), 0
    raise ValueError(f"unknown command '{command}'")


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
    lines.append(f"search 5 -> found 5 at index {index} after {comparisons} comparisons")
    lines.append("histogram:")
    lines.extend(build_histogram(numbers))
    return lines


def usage():
    """Return the one-block usage string."""
    return (
        "usage: python3 patterns.py <command> [arg]\n"
        "  commands (read numbers from stdin, except demo):\n"
        "    demo, total, filter <threshold>, transform, search <target>, histogram"
    )


def main(argv):
    """Entry point. Returns an exit code: 0 on success, non-zero on error."""
    if len(argv) < 2:
        print("error: no command given", file=sys.stderr)
        print(usage(), file=sys.stderr)
        return 1
    command, args = argv[1], argv[2:]
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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
