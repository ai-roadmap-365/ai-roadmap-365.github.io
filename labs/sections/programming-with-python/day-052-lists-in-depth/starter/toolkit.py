#!/usr/bin/env python3
"""List Toolkit — YOUR working file.

Build this program one exercise at a time. Each numbered exercise below
names exactly what to write. The finished reference is in
examples/toolkit.py — try each exercise yourself before peeking.

The golden rule for every function here: return a NEW list, and never change
the list you were given. Copy before you mutate.

When all five exercises are done, run:
    python3 starter/toolkit.py
    bash tests/run_tests.sh
"""
import sys


def dedupe(items):
    """Return a new list with duplicates removed, preserving first-seen order."""
    # Exercise 1: DEDUPE.
    # Build an empty result list. Loop over items; append an item only if it
    # is not already `in` result. Return result.
    # Verify by hand: dedupe([1, 1, 2, 1, 3]) must be [1, 2, 3].
    raise NotImplementedError("Exercise 1: implement dedupe")


def flatten(matrix):
    """Flatten one level of nesting: a list of lists into a single new list."""
    # Exercise 2: FLATTEN.
    # Build an empty result list. Loop over each row in matrix; loop over each
    # item in that row; append the item to result. Return result.
    # Verify by hand: flatten([[1, 2], [3, 4]]) must be [1, 2, 3, 4].
    raise NotImplementedError("Exercise 2: implement flatten")


def sort_by_length(words):
    """Return a NEW list of words sorted by length, shortest first."""
    # Exercise 3: SORT WITH A KEY.
    # Return sorted(words, key=len). `sorted` returns a new list and leaves
    # `words` untouched; the sort is stable, so equal-length words keep order.
    raise NotImplementedError("Exercise 3: implement sort_by_length")


def top_n(numbers, n):
    """Return the n largest numbers, highest first, as a new list."""
    # Exercise 4: SORT THEN SLICE.
    # Sort a copy in descending order (sorted(numbers, reverse=True)), then
    # slice off the first n with [:n]. Return that slice.
    raise NotImplementedError("Exercise 4: implement top_n")


def with_appended(items, value):
    """Return a NEW list equal to items plus value; the input is unchanged."""
    # Exercise 5: COPY BEFORE YOU MUTATE.
    # Make a shallow copy first: result = items[:]. Append value to result.
    # Return result. Do NOT append to `items` directly — that would change the
    # caller's list, the exact bug this lesson is about.
    raise NotImplementedError("Exercise 5: implement with_appended")


def main(argv):
    """Run the demo pipeline over a sample dataset. Returns exit code 0."""
    scores = [88, 72, 95, 72, 60, 95, 81]
    print(f"built:    {scores}")
    print(f"top 3:    {top_n(scores, 3)}")
    print(f"stride:   {scores[::2]}")
    print(f"last 2:   {scores[-2:]}")
    words = ["pear", "fig", "apple", "kiwi", "plum", "fig"]
    print(f"by len:   {sort_by_length(words)}")
    print(f"unique:   {dedupe(words)}")
    matrix = [[1, 2, 3], [4, 5, 6]]
    print(f"flat:     {flatten(matrix)}")
    original = [10, 20, 30]
    grown = with_appended(original, 40)
    print(f"grown:    {grown}")
    print(f"original: {original}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
