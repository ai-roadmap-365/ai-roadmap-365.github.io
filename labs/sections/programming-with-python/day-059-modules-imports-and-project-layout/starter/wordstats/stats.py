"""stats.py — one responsibility: turn a list of words into frequency numbers.

Depends only on the standard library; does not import its siblings. Plain
lists in, plain values out. The reference is in ``examples/wordstats/stats.py``.
"""
from collections import Counter


def count_words(words):
    """Return a plain dict mapping each word to how many times it appears."""
    # Exercise 2: COUNT WORDS.
    # Return dict(Counter(words)) — a normal dict of word -> count.
    raise NotImplementedError("Exercise 2: implement count_words")


def top_n(words, n=5):
    """Return the n most common (word, count) pairs, most frequent first."""
    # Exercise 3: TOP N.
    # 1. counts = count_words(words)
    # 2. Sort counts.items() by count DESCENDING, then word ASCENDING, so ties
    #    break alphabetically and the result is deterministic:
    #        sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    # 3. Return the first n of that sorted list.
    raise NotImplementedError("Exercise 3: implement top_n")
