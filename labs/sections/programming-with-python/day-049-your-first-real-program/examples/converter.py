#!/usr/bin/env python3
"""Convert a temperature between Celsius and Fahrenheit.

This is a complete, small, real program: it reads input from the command
line, validates it, does one useful job, prints clear output, and fails
gracefully (a readable message and a non-zero exit code) on bad input.

Usage:
    python3 converter.py <value> <unit>

<value> is a number; <unit> is the unit you are converting FROM: C or F.

Examples:
    python3 converter.py 100 C   ->  100.0 C = 212.0 F
    python3 converter.py 32 F    ->  32.0 F = 0.0 C
"""
import sys

# Coldest physically possible temperature, used as a sanity-check edge case.
ABSOLUTE_ZERO_C = -273.15


def celsius_to_fahrenheit(celsius):
    """Return the Fahrenheit equivalent of a Celsius temperature."""
    return celsius * 9 / 5 + 32


def fahrenheit_to_celsius(fahrenheit):
    """Return the Celsius equivalent of a Fahrenheit temperature."""
    return (fahrenheit - 32) * 5 / 9


def parse_args(args):
    """Validate raw [value, unit] arguments and return (number, unit).

    Raises ValueError with a human-readable message on any bad input:
    wrong argument count, a non-numeric value, an unknown unit, or a
    temperature below absolute zero.
    """
    if len(args) != 2:
        raise ValueError("expected 2 arguments: <value> <unit> (e.g. 100 C)")
    value_text, unit_text = args
    try:
        value = float(value_text)
    except ValueError:
        raise ValueError(f"'{value_text}' is not a number")
    unit = unit_text.strip().upper()
    if unit not in ("C", "F"):
        raise ValueError(f"unit must be C or F, not '{unit_text}'")
    limit = ABSOLUTE_ZERO_C if unit == "C" else celsius_to_fahrenheit(ABSOLUTE_ZERO_C)
    if value < limit:
        raise ValueError(f"{value} {unit} is below absolute zero")
    return value, unit


def convert(value, unit):
    """Convert value from unit to the other unit; return (result, result_unit)."""
    if unit == "C":
        return celsius_to_fahrenheit(value), "F"
    return fahrenheit_to_celsius(value), "C"


def format_result(value, unit, result, result_unit):
    """Return the one-line, human-readable result string."""
    return f"{value:.1f} {unit} = {result:.1f} {result_unit}"


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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
