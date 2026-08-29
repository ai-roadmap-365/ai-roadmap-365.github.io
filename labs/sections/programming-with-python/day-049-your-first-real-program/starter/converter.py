#!/usr/bin/env python3
"""Temperature converter — YOUR working file.

Build this program one exercise at a time. Each numbered exercise below
names exactly what to write. The finished reference is in
examples/converter.py — try each exercise yourself before peeking.

When you have completed all five exercises, this file should behave just
like the reference:

    python3 starter/converter.py 100 C   ->  100.0 C = 212.0 F
    python3 starter/converter.py hot C   ->  error (exit code 1)

Then run:  bash tests/run_tests.sh
"""
import sys

ABSOLUTE_ZERO_C = -273.15


def celsius_to_fahrenheit(celsius):
    """Return the Fahrenheit equivalent of a Celsius temperature."""
    # Exercise 1: WRITE A FUNCTION.
    # Return the Fahrenheit value: multiply by 9, divide by 5, add 32.
    # Verify by hand: celsius_to_fahrenheit(100) must be 212.0.
    raise NotImplementedError("Exercise 1: implement celsius_to_fahrenheit")


def fahrenheit_to_celsius(fahrenheit):
    """Return the Celsius equivalent of a Fahrenheit temperature."""
    # (Provided so the program is complete once Exercise 1 is done.)
    return (fahrenheit - 32) * 5 / 9


def parse_args(args):
    """Validate raw [value, unit] arguments and return (number, unit)."""
    # Exercise 3: VALIDATE INPUT.
    # 1. If len(args) != 2, raise ValueError with a clear message.
    # 2. Convert args[0] to float inside try/except; on failure raise
    #    ValueError(f"'{args[0]}' is not a number").
    # 3. Normalize args[1] with .strip().upper(); if it is not "C" or "F",
    #    raise ValueError naming the allowed units.
    # Exercise 5: HANDLE AN EDGE CASE.
    # 4. Reject temperatures below absolute zero (use ABSOLUTE_ZERO_C for C,
    #    and celsius_to_fahrenheit(ABSOLUTE_ZERO_C) for F).
    # Return (value, unit).
    raise NotImplementedError("Exercises 3 & 5: implement parse_args")


def convert(value, unit):
    """Convert value from unit to the other unit; return (result, result_unit)."""
    # (Provided.)
    if unit == "C":
        return celsius_to_fahrenheit(value), "F"
    return fahrenheit_to_celsius(value), "C"


def format_result(value, unit, result, result_unit):
    """Return the one-line, human-readable result string."""
    # Exercise 4: FORMAT OUTPUT.
    # Return an f-string like "100.0 C = 212.0 F", showing each number to
    # one decimal place (use the :.1f format specifier).
    raise NotImplementedError("Exercise 4: implement format_result")


def main(argv):
    """Program entry point. Returns an exit code: 0 on success, 1 on bad input."""
    try:
        value, unit = parse_args(argv[1:])
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        print("usage: python3 converter.py <value> <unit>   (unit is C or F)",
              file=sys.stderr)
        return 1
    result, result_unit = convert(value, unit)
    print(format_result(value, unit, result, result_unit))
    return 0


# Exercise 2: ADD THE MAIN GUARD.
# Below this comment, add the guard so the program runs only when this file
# is executed directly (not when it is imported):
#
#     if __name__ == "__main__":
#         sys.exit(main(sys.argv))
