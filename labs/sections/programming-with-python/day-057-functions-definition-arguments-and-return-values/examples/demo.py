#!/usr/bin/env python3
"""demo.py — drive the function library and use its return values.

Run this from the lab directory to see the library in action:

    python3 examples/demo.py

It imports the pure functions from library.py and *uses what they return* —
composing calls, unpacking a returned tuple, and passing keyword arguments —
without any function printing on its own. All the printing happens here, in
the caller, which is exactly the pure-function-plus-thin-shell shape the
lesson teaches.
"""
import sys
from pathlib import Path

# Make the sibling library.py importable no matter where this is run from.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from library import (
    clamp,
    greet,
    is_palindrome,
    mean,
    normalize_whitespace,
    reverse_words,
    summarize,
    tally,
    word_count,
)


def main():
    """Call the library functions and print how their return values are used."""
    sentence = "  the  quick   brown fox  "
    clean = normalize_whitespace(sentence)
    print(f"normalize_whitespace -> {clean!r}")
    print(f"word_count           -> {word_count(clean)}")
    print(f"reverse_words        -> {reverse_words(clean)!r}")

    print(f"is_palindrome('Racecar')        -> {is_palindrome('Racecar')}")
    print(f"is_palindrome('function')       -> {is_palindrome('function')}")

    # Default vs keyword arguments.
    print(f"greet('Ada')                    -> {greet('Ada')!r}")
    print(f"greet('Grace', 'Welcome')       -> {greet('Grace', 'Welcome')!r}")
    print(f"greet('Alan', punctuation='.')  -> {greet('Alan', punctuation='.')!r}")

    # Default arguments on clamp.
    print(f"clamp(1.5)                      -> {clamp(1.5)}")
    print(f"clamp(42, high=100)             -> {clamp(42, high=100)}")

    # Unpacking a returned tuple of several results.
    readings = [7, 3, 9, 4, 6]
    count, total, low, high, average = summarize(readings)
    print(f"summarize({readings}) ->")
    print(f"    count={count} total={total} min={low} max={high} mean={average}")
    print(f"mean(readings)                  -> {mean(readings)}")

    # Purity of tally: two calls do not leak state into each other.
    print(f"tally(['a','b','a'])            -> {tally(['a', 'b', 'a'])}")
    print(f"tally(['x'])                    -> {tally(['x'])}")


if __name__ == "__main__":
    main()
