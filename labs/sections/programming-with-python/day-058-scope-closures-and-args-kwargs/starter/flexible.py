#!/usr/bin/env python3
"""flexible.py — YOUR working file.

Build these flexible functions one exercise at a time. Each numbered exercise
below names exactly what to write. The finished reference is in
examples/flexible.py — try each exercise yourself before peeking.

When all five exercises are done, running this file prints the same demo as
the reference:

    python3 starter/flexible.py

Then run:  bash tests/run_tests.sh
"""

# Module-level (global) defaults, provided. build_request fills these in when
# the caller does not override them. They mirror LLM generation settings.
DEFAULTS = {"temperature": 0.7, "max_tokens": 256, "model": "demo"}


def total(*numbers):
    """Return the sum of any number of positional arguments."""
    # Exercise 1: VARIADIC POSITIONAL ARGUMENTS.
    # *numbers gathers every positional argument into a tuple. Return their
    # sum. Hint: sum() of an empty tuple is 0, so total() should return 0
    # with no special case.
    raise NotImplementedError("Exercise 1: implement total")


def average(*numbers, ndigits=2):
    """Return the mean of the numbers, rounded to ndigits (keyword-only)."""
    # Exercise 2: A KEYWORD-ONLY ARGUMENT.
    # ndigits sits after *numbers, so it is keyword-only. If there are no
    # numbers, return 0.0. Otherwise return round(sum(numbers)/len(numbers),
    # ndigits).
    raise NotImplementedError("Exercise 2: implement average")


def make_counter(start=0, step=1):
    """Return a function yielding start, start+step, start+2*step, ..."""
    # Exercise 3: A CLOSURE WITH PRIVATE STATE.
    # 1. Set count = start.
    # 2. Define an inner function counter() that:
    #      - declares 'nonlocal count' (so it rebinds the enclosing count),
    #      - remembers the current value, adds step to count, returns the
    #        remembered value.
    # 3. Return the inner counter function (do NOT call it here).
    raise NotImplementedError("Exercise 3: implement make_counter")


def make_multiplier(factor):
    """Return a function that multiplies its argument by the captured factor."""
    # Exercise 4: A CLOSURE FACTORY.
    # Define an inner function multiply(n) that returns n * factor (factor is
    # captured from this enclosing scope), then return multiply.
    raise NotImplementedError("Exercise 4: implement make_multiplier")


def build_request(prompt, **kwargs):
    """Merge caller keyword arguments over DEFAULTS (the ML config pattern)."""
    # Exercise 5: **kwargs CONFIG MERGE.
    # 1. **kwargs gathers extra keyword arguments into a dict.
    # 2. Build config = {**DEFAULTS, **kwargs} so the caller's values win
    #    (they are spread last).
    # 3. Return {"prompt": prompt, **config}.
    raise NotImplementedError("Exercise 5: implement build_request")


def main():
    """Print a short, deterministic demonstration of every function. (Provided.)"""
    print(f"total() -> {total()}")
    print(f"total(2, 4, 6) -> {total(2, 4, 6)}")
    print(f"average(10, 20, 30) -> {average(10, 20, 30)}")
    print(f"average(1, 2, 3, ndigits=4) -> {average(1, 2, 3, ndigits=4)}")

    counter = make_counter()
    print(f"counter: {counter()} {counter()} {counter()} {counter()}")
    other = make_counter(100)
    print(f"second counter is independent: {other()}")

    triple = make_multiplier(3)
    tenfold = make_multiplier(10)
    print(f"triple(5) -> {triple(5)} ; tenfold(5) -> {tenfold(5)}")

    default_request = build_request("hello")
    print(f"build_request('hello') -> {default_request}")
    overridden = build_request("hello", temperature=0.2)
    print(
        "build_request('hello', temperature=0.2) -> "
        f"temperature={overridden['temperature']}, model={overridden['model']}"
    )
    return 0


if __name__ == "__main__":
    main()
