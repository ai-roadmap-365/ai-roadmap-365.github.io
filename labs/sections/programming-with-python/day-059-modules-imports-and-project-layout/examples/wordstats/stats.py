"""stats.py — one responsibility: turn a list of words into frequency numbers.

Like ``tokens``, this module depends only on the standard library and does not
import its siblings. It takes plain Python lists in and returns plain Python
values out, so it can be imported and tested on its own.
"""
from collections import Counter


def count_words(words):
    """Return a plain dict mapping each word to how many times it appears."""
    return dict(Counter(words))


def top_n(words, n=5):
    """Return the n most common (word, count) pairs, most frequent first.

    Ties are broken alphabetically so the result is deterministic on every
    machine. ``top_n(["a", "b", "a"], 1)`` returns ``[('a', 2)]``.
    """
    counts = count_words(words)
    ordered = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ordered[:n]
