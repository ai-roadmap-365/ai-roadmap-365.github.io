#!/usr/bin/env python3
"""Decision engine: classify a model prediction into ACCEPT / REVIEW / REJECT.

This is a complete, small, real program that shows every idea from the Day 50
lesson working together: comparison operators, the logical `and` with
short-circuit evaluation, an `if`/`elif`/`else`-style ladder, a guard clause,
a chained comparison for range validation, and a (nested) conditional
expression. It reads its input from the command line, validates it, does one
useful job, prints clear output, and fails gracefully on bad input.

Usage:
    python3 triage.py <score> <status>

<score>  is the model's confidence, a number from 0.0 to 1.0.
<status> is whether an upstream check passed: verified or unverified.

Examples:
    python3 triage.py 0.95 verified     ->  AUTO_ACCEPT
    python3 triage.py 0.95 unverified   ->  REVIEW
    python3 triage.py 0.30 verified     ->  REJECT
"""
import sys

VALID_STATUSES = ("verified", "unverified")


def confidence_band(score):
    """Return 'high', 'medium', or 'low' for a score in 0.0-1.0.

    A three-way choice written as a nested conditional (ternary) expression.
    """
    return "high" if score >= 0.9 else ("medium" if score >= 0.5 else "low")


def classify(score, verified):
    """Return the routing decision for a prediction.

    Uses a guard clause to reject low confidence first, then the logical
    `and` (which short-circuits) to auto-accept only what is both confident
    and verified, and falls through to REVIEW for everything else.
    """
    if score < 0.5:                       # guard clause: turn away low confidence
        return "REJECT"
    if score >= 0.9 and verified:         # confident AND checked: safe to accept
        return "AUTO_ACCEPT"
    return "REVIEW"                        # medium confidence, or high-but-unverified


def parse_args(args):
    """Validate raw [score, status] arguments and return (float, bool).

    Raises ValueError with a human-readable message on any bad input:
    wrong argument count, a non-numeric score, an unknown status, or a
    score outside the 0.0-1.0 range.
    """
    if len(args) != 2:
        raise ValueError("expected 2 arguments: <score> <status> (e.g. 0.95 verified)")
    score_text, status_text = args
    try:
        score = float(score_text)
    except ValueError:
        raise ValueError(f"'{score_text}' is not a number")
    status = status_text.strip().lower()
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be verified or unverified, not '{status_text}'")
    if not 0.0 <= score <= 1.0:           # chained comparison: range check
        raise ValueError(f"score {score} is out of range (expected 0.0 to 1.0)")
    verified = status == "verified"
    return score, verified


def format_result(score, verified, category, band):
    """Return the one-line, human-readable decision string."""
    return f"score={score:.2f} verified={str(verified):<5} -> {category} (confidence: {band})"


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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
