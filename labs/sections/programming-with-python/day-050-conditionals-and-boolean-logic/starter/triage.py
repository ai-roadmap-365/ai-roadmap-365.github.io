#!/usr/bin/env python3
"""Decision engine — YOUR working file.

Build this program one exercise at a time. Each numbered exercise below names
exactly what to write, using the boolean logic from the Day 50 lesson. The
finished reference is in examples/triage.py — try each exercise yourself
before peeking.

When you have completed all five exercises, this file should behave just like
the reference:

    python3 starter/triage.py 0.95 verified   ->  ... AUTO_ACCEPT (confidence: high)
    python3 starter/triage.py 1.5 verified    ->  error (exit code 2)

Then run:  bash tests/run_tests.sh
"""
import sys

VALID_STATUSES = ("verified", "unverified")


def confidence_band(score):
    """Return 'high', 'medium', or 'low' for a score in 0.0-1.0."""
    # Exercise 1: WRITE A NESTED TERNARY (conditional expression).
    # Return "high" when score >= 0.9, "medium" when score >= 0.5,
    # otherwise "low". Do it in one line:
    #   return "high" if score >= 0.9 else ("medium" if score >= 0.5 else "low")
    # Verify by hand: confidence_band(0.5) must be "medium".
    raise NotImplementedError("Exercise 1: implement confidence_band")


def classify(score, verified):
    """Return the routing decision: REJECT, AUTO_ACCEPT, or REVIEW."""
    # Exercise 2: WRITE THE CLASSIFICATION LADDER.
    # 1. Guard clause: if score < 0.5, return "REJECT" immediately.
    # 2. If score >= 0.9 AND verified, return "AUTO_ACCEPT"
    #    (note the logical `and` short-circuits: verified is only checked
    #     when score >= 0.9 is already True).
    # 3. Otherwise return "REVIEW".
    raise NotImplementedError("Exercise 2: implement classify")


def parse_args(args):
    """Validate raw [score, status] arguments and return (float, bool)."""
    # Exercise 3: VALIDATE INPUT (guard the boundary).
    # 1. If len(args) != 2, raise ValueError with a clear message.
    # 2. Convert args[0] to float inside try/except; on failure raise
    #    ValueError(f"'{args[0]}' is not a number").
    # 3. Normalise args[1] with .strip().lower(); if it is not in
    #    VALID_STATUSES, raise ValueError naming the allowed statuses.
    # 4. Use a CHAINED COMPARISON to reject an out-of-range score:
    #    if not 0.0 <= score <= 1.0: raise ValueError(...).
    # 5. Return (score, status == "verified").
    raise NotImplementedError("Exercise 3: implement parse_args")


def format_result(score, verified, category, band):
    """Return the one-line, human-readable decision string."""
    # Exercise 4: FORMAT OUTPUT.
    # Return an f-string like:
    #   score=0.95 verified=True  -> AUTO_ACCEPT (confidence: high)
    # Show the score to two decimals (:.2f) and left-pad the verified flag
    # to width 5 so True and False line up: {str(verified):<5}.
    raise NotImplementedError("Exercise 4: implement format_result")


def main(argv):
    """Program entry point. Returns an exit code: 0 on success, 2 on bad input."""
    try:
        score, verified = parse_args(argv[1:])
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        print("usage: python3 triage.py <score> <status>   "
              "(score 0.0-1.0, status verified|unverified)", file=sys.stderr)
        return 2
    category = classify(score, verified)
    band = confidence_band(score)
    print(format_result(score, verified, category, band))
    return 0


# Exercise 5: ADD THE MAIN GUARD.
# Below this comment, add the guard so the program runs only when this file
# is executed directly (not when it is imported):
#
#     if __name__ == "__main__":
#         sys.exit(main(sys.argv))
