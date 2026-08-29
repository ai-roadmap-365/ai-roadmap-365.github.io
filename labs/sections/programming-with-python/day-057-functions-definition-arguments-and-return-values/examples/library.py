#!/usr/bin/env python3
"""library.py — a small library of well-documented, pure functions.

Every function here takes its input as arguments and hands back a *return
value*; none of them read the keyboard, print results, or change anything
outside themselves. That makes them "pure": for the same arguments they
give the same answer, and calling them has no side effects. Pure functions
are the easy ones to test, because a test just calls the function and
checks what comes back.

The module is a grab-bag of tiny text and number utilities that together
show every idea from the Day 57 lesson:

    - def syntax and a good docstring on every function
    - positional, keyword, and default arguments      (greet, clamp)
    - a return value the caller uses, and the implicit None
    - returning a tuple to hand back several results   (summarize)
    - the mutable-default-argument trap, avoided with None (tally)

Import it and call the functions; nothing runs on import, because there is
no top-level code — only definitions. See examples/demo.py for a session
that calls these functions and uses their return values.
"""


def word_count(text):
    """Return the number of whitespace-separated words in text.

    >>> word_count("the quick brown fox")
    4
    >>> word_count("   ")
    0
    """
    return len(text.split())


def normalize_whitespace(text):
    """Return text with every run of whitespace collapsed to one space and
    the ends stripped.

    >>> normalize_whitespace("  hello   world  ")
    'hello world'
    """
    return " ".join(text.split())


def reverse_words(text):
    """Return text with its words in reverse order.

    >>> reverse_words("one two three")
    'three two one'
    """
    return " ".join(reversed(text.split()))


def is_palindrome(text):
    """Return True if text reads the same forwards and backwards, ignoring
    case and any character that is not a letter or digit.

    >>> is_palindrome("A man, a plan, a canal: Panama")
    True
    >>> is_palindrome("hello")
    False
    """
    cleaned = [character.lower() for character in text if character.isalnum()]
    return cleaned == cleaned[::-1]


def celsius_to_fahrenheit(celsius):
    """Return the Fahrenheit value for a Celsius temperature.

    >>> celsius_to_fahrenheit(100)
    212.0
    >>> celsius_to_fahrenheit(0)
    32.0
    """
    return celsius * 9 / 5 + 32


def clamp(value, low=0.0, high=1.0):
    """Return value limited to the range [low, high].

    low and high are default arguments, so clamp(x) limits x to [0.0, 1.0],
    while clamp(x, -10, 10) uses your own range. Passing them by keyword —
    clamp(x, high=100) — is clearer at the call site than a bare number.

    >>> clamp(1.5)
    1.0
    >>> clamp(-3, low=-10, high=10)
    -3
    """
    if low > high:
        raise ValueError("low must not be greater than high")
    return max(low, min(value, high))


def mean(numbers):
    """Return the arithmetic mean of a sequence of numbers.

    Raises ValueError on an empty sequence, because the mean of nothing is
    undefined — a clear error is better than a hidden division by zero.

    >>> mean([2, 4, 6])
    4.0
    """
    if not numbers:
        raise ValueError("mean of an empty sequence is undefined")
    return sum(numbers) / len(numbers)


def summarize(numbers):
    """Return a tuple (count, total, minimum, maximum, mean) for numbers.

    This is the multiple-results pattern: instead of five separate function
    calls that each re-scan the data, one call hands back a tuple the caller
    can unpack:

        count, total, low, high, average = summarize(readings)

    Raises ValueError on an empty sequence.

    >>> summarize([2, 4, 6])
    (3, 12, 2, 6, 4.0)
    """
    if not numbers:
        raise ValueError("cannot summarize an empty sequence")
    count = len(numbers)
    total = sum(numbers)
    return (count, total, min(numbers), max(numbers), total / count)


def greet(name, greeting="Hello", punctuation="!"):
    """Return a greeting line for name.

    name is required (positional); greeting and punctuation have defaults.
    All three can be passed by position or by keyword, so every call below
    is valid:

        greet("Ada")                       -> 'Hello, Ada!'
        greet("Ada", "Welcome")            -> 'Welcome, Ada!'
        greet("Ada", punctuation=".")      -> 'Hello, Ada.'

    >>> greet("Ada")
    'Hello, Ada!'
    >>> greet("Grace", greeting="Welcome", punctuation=".")
    'Welcome, Grace.'
    """
    return f"{greeting}, {name}{punctuation}"


def tally(items, counts=None):
    """Return a frequency dict counting how often each item appears.

    The default for counts is None, NOT {}. A mutable default (counts={})
    would be created once when the function is defined and then SHARED
    across every call, so counts would remember items from previous calls —
    the classic mutable-default-argument bug. Using None and building a
    fresh dict inside avoids it. When a starting tally is passed in, it is
    copied rather than mutated, so this function stays pure.

    >>> tally(["a", "b", "a"])
    {'a': 2, 'b': 1}
    >>> tally(["a"], {"a": 5})
    {'a': 6}
    """
    result = dict(counts) if counts is not None else {}
    for item in items:
        result[item] = result.get(item, 0) + 1
    return result
