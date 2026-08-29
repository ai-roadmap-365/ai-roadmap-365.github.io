#!/usr/bin/env python3
"""List Toolkit — five idiomatic list operations, plus a demo pipeline.

This is a complete, small, real program: it exposes a handful of pure list
functions and a `main` that runs them over a sample dataset, printing each
step so you can watch a list being built, sliced, sorted, and transformed.

Every function here returns a NEW list and never changes the list it is
given — that discipline (copy before you mutate) is the whole point of the
lesson, because silent list mutation is one of the most common bugs in
data and machine-learning code.

Usage:
    python3 toolkit.py            # run the demo pipeline

Import and reuse any function:
    from toolkit import dedupe, flatten, sort_by_length, top_n, with_appended
"""
import sys


def dedupe(items):
    """Return a new list with duplicates removed, preserving first-seen order.

    Uses list membership (`in`), which scans the growing result — clear and
    correct. A set would make the membership test faster; you meet sets on
    Day 54.
    """
    result = []
    for item in items:
        if item not in result:      # membership test on a list is O(n)
            result.append(item)
    return result


def flatten(matrix):
    """Flatten one level of nesting: a list of lists into a single new list.

    flatten([[1, 2], [3, 4]]) -> [1, 2, 3, 4]
    """
    result = []
    for row in matrix:
        for item in row:            # iterate the inner list
            result.append(item)
    return result


def sort_by_length(words):
    """Return a NEW list of words sorted by length, shortest first.

    `sorted` returns a new list and leaves the input untouched. The sort is
    stable, so words of equal length keep their original relative order.
    """
    return sorted(words, key=len)


def top_n(numbers, n):
    """Return the n largest numbers, highest first, as a new list.

    Sort a copy in descending order, then slice off the first n.
    """
    return sorted(numbers, reverse=True)[:n]


def with_appended(items, value):
    """Return a NEW list equal to items plus value; the input is unchanged.

    `items[:]` makes a shallow copy first, so appending touches only the copy
    — the caller's original list is protected from surprise mutation.
    """
    result = items[:]               # shallow copy protects the caller's list
    result.append(value)
    return result


def main(argv):
    """Run the demo pipeline over a sample dataset. Returns exit code 0."""
    # BUILD a list of exam scores.
    scores = [88, 72, 95, 72, 60, 95, 81]
    print(f"built:    {scores}")

    # SLICE: top three (sort then slice), every other item, the last two.
    print(f"top 3:    {top_n(scores, 3)}")
    print(f"stride:   {scores[::2]}")
    print(f"last 2:   {scores[-2:]}")

    # SORT with a key: order words by length, stably.
    words = ["pear", "fig", "apple", "kiwi", "plum", "fig"]
    print(f"by len:   {sort_by_length(words)}")

    # TRANSFORM: remove duplicates (order kept) and flatten a matrix.
    print(f"unique:   {dedupe(words)}")
    matrix = [[1, 2, 3], [4, 5, 6]]
    print(f"flat:     {flatten(matrix)}")

    # SAFE COPY: grow a copy, then prove the original was not touched.
    original = [10, 20, 30]
    grown = with_appended(original, 40)
    print(f"grown:    {grown}")
    print(f"original: {original}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
