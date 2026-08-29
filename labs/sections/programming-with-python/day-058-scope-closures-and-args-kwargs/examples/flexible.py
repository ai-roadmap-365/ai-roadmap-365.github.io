#!/usr/bin/env python3
"""flexible.py — flexible functions with *args, **kwargs, and closures.

A small, self-contained module that demonstrates the Day 58 ideas as working,
testable functions:

  * total(*numbers)               -- variadic positional arguments
  * average(*numbers, ndigits=2)  -- a keyword-only argument
  * make_counter(start, step)     -- a closure with private, remembered state
  * make_multiplier(factor)       -- a closure factory
  * build_request(prompt, **kw)   -- the **kwargs config-merge pattern used by
                                     nearly every ML/LLM library

Every input comes from function arguments (never an interactive prompt), so
the module is fully importable and testable. Run it directly to see a demo:

    python3 flexible.py

Or import a function and use it on its own:

    python3 -c "import sys; sys.path.insert(0, 'examples'); \
from flexible import make_counter; c = make_counter(); print(c(), c(), c())"
"""

# Module-level (global) defaults — the "building stockroom" of settings that
# build_request fills in when the caller does not override them. These mirror
# the generation settings a real LLM call takes (temperature, token budget).
DEFAULTS = {"temperature": 0.7, "max_tokens": 256, "model": "demo"}


def total(*numbers):
    """Return the sum of any number of positional arguments.

    *numbers gathers every positional argument into a tuple, so total() is 0,
    total(5) is 5, and total(2, 4, 6) is 12. Because sum() of an empty tuple
    is 0, the empty case needs no special handling.
    """
    return sum(numbers)


def average(*numbers, ndigits=2):
    """Return the mean of the given numbers, rounded to ndigits.

    ndigits is keyword-only: it sits after the *numbers gather, so it can only
    be passed by name (average(1, 2, 3, ndigits=4)) and a stray positional
    number can never be mistaken for it. An empty call returns 0.0.
    """
    if not numbers:
        return 0.0
    return round(sum(numbers) / len(numbers), ndigits)


def make_counter(start=0, step=1):
    """Return a function that yields start, start+step, start+2*step, ...

    This is a closure: the inner counter() captures the enclosing 'count'
    variable and, via 'nonlocal', updates it in place. Each call to
    make_counter builds a fresh, independent 'count', so two counters never
    interfere with each other.
    """
    count = start

    def counter():
        nonlocal count            # rebind the enclosing count, not a new local
        value = count
        count += step
        return value

    return counter


def make_multiplier(factor):
    """Return a function that multiplies its argument by the captured factor.

    make_multiplier(3) returns a 'triple' function and make_multiplier(10)
    returns a 'tenfold' function; each remembers its own 'factor' because the
    inner multiply() closes over the enclosing scope.
    """
    def multiply(n):
        return n * factor         # 'factor' comes from the enclosing scope

    return multiply


def build_request(prompt, **kwargs):
    """Merge caller keyword arguments over DEFAULTS — the ML config pattern.

    **kwargs gathers every extra keyword argument into a dict. Spreading
    {**DEFAULTS, **kwargs} builds a new dict where the caller's values win,
    because they are applied last. This is exactly how a high-level helper
    accepts generation settings and forwards them to a real model call.
    """
    config = {**DEFAULTS, **kwargs}
    return {"prompt": prompt, **config}


def main():
    """Print a short, deterministic demonstration of every function."""
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
