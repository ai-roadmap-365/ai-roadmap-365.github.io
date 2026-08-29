#!/usr/bin/env python3
"""library.py — YOUR working file: a library of pure functions.

Build this function library one exercise at a time. Each numbered exercise
names exactly what to write, including the docstring it must carry. The
finished reference is in examples/library.py — try each exercise yourself
before peeking.

Rules for every function you write here:
    - Give it a docstring: one line saying what it RETURNS, then a short
      example. The tests check that each public function has a docstring.
    - Make it PURE: take input only from the arguments, return a value, and
      do not print or change anything outside the function.

When all six exercises are done, run:  bash tests/run_tests.sh
"""


def word_count(text):
    """Return the number of whitespace-separated words in text.

    >>> word_count("the quick brown fox")
    4
    """
    # Exercise 1: RETURN A VALUE.
    # Split text on whitespace with text.split() and return how many pieces
    # there are (use len). Do not print — return the number.
    raise NotImplementedError("Exercise 1: implement word_count")


def normalize_whitespace(text):
    """Return text with runs of whitespace collapsed to one space and the
    ends stripped. (Provided as a worked example — read it, then match its
    shape in your own functions.)

    >>> normalize_whitespace("  hello   world  ")
    'hello world'
    """
    return " ".join(text.split())


def reverse_words(text):
    """Return text with its words in reverse order.

    >>> reverse_words("one two three")
    'three two one'
    """
    # Exercise 2: BUILD AND RETURN A STRING.
    # Split text into words, reverse the list (reversed(...) or [::-1]), and
    # join the words back with a single space. Return the joined string.
    raise NotImplementedError("Exercise 2: implement reverse_words")


def celsius_to_fahrenheit(celsius):
    """Return the Fahrenheit value for a Celsius temperature.

    >>> celsius_to_fahrenheit(100)
    212.0
    """
    # Exercise 3: ONE PARAMETER, ONE RETURN.
    # Apply the formula celsius * 9 / 5 + 32 and return the result.
    raise NotImplementedError("Exercise 3: implement celsius_to_fahrenheit")


def clamp(value, low=0.0, high=1.0):
    """Return value limited to the range [low, high], using DEFAULT arguments
    so clamp(x) limits to [0.0, 1.0].

    >>> clamp(1.5)
    1.0
    >>> clamp(-3, low=-10, high=10)
    -3
    """
    # Exercise 4: DEFAULT ARGUMENTS.
    # low and high already have defaults in the signature above — do not
    # change them. Return the value pulled back into range:
    #     max(low, min(value, high))
    raise NotImplementedError("Exercise 4: implement clamp")


def summarize(numbers):
    """Return a tuple (count, total, minimum, maximum, mean) for numbers.

    >>> summarize([2, 4, 6])
    (3, 12, 2, 6, 4.0)
    """
    # Exercise 5: RETURN A TUPLE OF SEVERAL RESULTS.
    # 1. If numbers is empty, raise ValueError("cannot summarize an empty
    #    sequence").
    # 2. Otherwise compute count (len), total (sum), min, max, and the mean
    #    (total / count), and return them as a 5-tuple in that order.
    raise NotImplementedError("Exercise 5: implement summarize")


def tally(items, counts=None):
    """Return a frequency dict counting how often each item appears.

    The default for counts is None, NOT {} — a mutable default would be
    shared across calls and remember old items. Build a fresh dict inside.

    >>> tally(["a", "b", "a"])
    {'a': 2, 'b': 1}
    >>> tally(["a"], {"a": 5})
    {'a': 6}
    """
    # Exercise 6: AVOID THE MUTABLE-DEFAULT TRAP.
    # 1. Start result as a COPY of counts when counts is not None
    #    (result = dict(counts)), otherwise an empty dict {}.
    # 2. For each item, do result[item] = result.get(item, 0) + 1.
    # 3. Return result. (Keep the None default — do not write counts={}.)
    raise NotImplementedError("Exercise 6: implement tally")
