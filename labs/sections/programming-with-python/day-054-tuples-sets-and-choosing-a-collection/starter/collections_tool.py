#!/usr/bin/env python3
"""Choosing Collections — YOUR working file.

Build this program one exercise at a time. Each numbered exercise below names
exactly what to write. The finished reference is in
examples/collections_tool.py — try each exercise yourself before peeking.

When you have completed all five exercises, this file should behave just like
the reference:

    python3 starter/collections_tool.py "apple,banana,apple" "banana,cherry"
      ->  a six-line report ending in the symmetric difference

Then run:  bash tests/run_tests.sh
"""
import sys
from collections import namedtuple

# An immutable record of one comparison (a tuple with named fields).
SetReport = namedtuple("SetReport", ["common", "only_in_a", "only_in_b", "symmetric"])


def parse_items(text):
    """Split a comma-separated string into a tuple of cleaned items."""
    # Exercise 1: RETURN AN IMMUTABLE TUPLE.
    # Split `text` on commas, strip spaces off each part, drop blank parts,
    # and return the result as a TUPLE (not a list), e.g.
    #   parse_items("apple, banana ,,apple") -> ("apple", "banana", "apple")
    raise NotImplementedError("Exercise 1: implement parse_items")


def dedupe(items):
    """Return the unique items as a sorted tuple (a set removes duplicates)."""
    # Exercise 2: DEDUPE WITH A SET.
    # Build a set from `items` to drop duplicates, sort it for a deterministic
    # order, and return a tuple, e.g.
    #   dedupe(("a", "a", "b")) -> ("a", "b")
    raise NotImplementedError("Exercise 2: implement dedupe")


def compare(a_items, b_items):
    """Compute set algebra between two item collections; return a SetReport."""
    # Exercise 3: SET ALGEBRA.
    # Turn each argument into a set, then build a SetReport of SORTED TUPLES:
    #   common    = a & b   (intersection)
    #   only_in_a = a - b   (difference)
    #   only_in_b = b - a   (difference)
    #   symmetric = a ^ b   (symmetric difference)
    # Return SetReport(common=..., only_in_a=..., only_in_b=..., symmetric=...).
    raise NotImplementedError("Exercise 3: implement compare")


def format_report(a_items, b_items, report):
    """Return the multi-line, human-readable report string."""
    # Exercise 4: FORMAT OUTPUT.
    # Build a six-line string. Use the helper below so empty groups read
    # "(none)" instead of a blank. The lines are (exact text matters):
    #   List A: <N> items read, <U> unique after dedupe
    #   List B: <N> items read, <U> unique after dedupe
    #   Common (A & B): <items>
    #   Only in A (A - B): <items>
    #   Only in B (B - A): <items>
    #   Symmetric difference (A ^ B): <items>
    # where N is len(a_items), U is len(set(a_items)), and <items> is the
    # comma-joined group from `report`. Return the lines joined by "\n".
    def show(values):
        return ", ".join(values) if values else "(none)"

    raise NotImplementedError("Exercise 4: implement format_report")


def main(argv):
    """Entry point. Returns an exit code: 0 on success, 1 on bad input."""
    if len(argv[1:]) != 2:
        print('error: expected 2 arguments: "<list A>" "<list B>"', file=sys.stderr)
        print('usage: python3 collections_tool.py "a,b,c" "b,c,d"', file=sys.stderr)
        return 1
    a_items = parse_items(argv[1])
    b_items = parse_items(argv[2])
    if not a_items or not b_items:
        print("error: each list must contain at least one item", file=sys.stderr)
        print('usage: python3 collections_tool.py "a,b,c" "b,c,d"', file=sys.stderr)
        return 1
    report = compare(a_items, b_items)
    print(format_report(a_items, b_items, report))
    return 0


# Exercise 5: ADD THE MAIN GUARD.
# Below this comment, add the guard so the program runs only when this file
# is executed directly (not when it is imported):
#
#     if __name__ == "__main__":
#         sys.exit(main(sys.argv))
