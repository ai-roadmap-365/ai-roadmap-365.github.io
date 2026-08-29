"""Small text statistics helpers — the FIXED reference module.

This is `starter/textstats.py` with its two bugs repaired. Two functions
differ, and both repairs are marked below with the comment `# repaired`.
Compare the two files once you have found the bugs yourself:

    diff starter/textstats.py examples/textstats.py

The docstrings are unchanged, because the docstrings were never wrong — the
code was. That is the usual shape of a bug: the specification was fine and
somebody's fingers were not.
"""

from __future__ import annotations

import math
import re

# A "word" is a run of letters, optionally containing apostrophes, so that
# "don't" is one word and "state-of-the-art" is four.
WORD_PATTERN = re.compile(r"[A-Za-z']+")


def words(text: str) -> list[str]:
    """Split text into lowercase words.

    Punctuation and digits are separators. The result is in reading order and
    may contain repeats.

        words("The cat. The hat!") -> ['the', 'cat', 'the', 'hat']
        words("")                  -> []
    """
    return [match.group(0).lower() for match in WORD_PATTERN.finditer(text)]


def word_count(text: str) -> int:
    """Count the words in text.

        word_count("The cat. The hat!") -> 4
        word_count("")                  -> 0
    """
    return len(words(text))


def average_word_length(text: str) -> float:
    """Mean number of characters per word, rounded to two decimal places.

    Empty text has no words, so the average is defined to be 0.0 — asking for
    the mean of nothing is not an error, it is just nothing.

        average_word_length("the cat")  -> 3.0
        average_word_length("")         -> 0.0
    """
    found = words(text)
    if not found:  # repaired: the mean of no words is 0.0, not a crash
        return 0.0
    total_characters = sum(len(word) for word in found)
    return round(total_characters / len(found), 2)


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    """The n most frequent words, most frequent first.

    Ties are broken alphabetically so the result is deterministic. Asking for
    more words than exist returns everything. Asking for zero returns nothing.

        top_words("a b a c a b", 2) -> [('a', 3), ('b', 2)]
        top_words("a b a c a b", 9) -> [('a', 3), ('b', 2), ('c', 1)]
        top_words("a b a c a b", 0) -> []
    """
    counts: dict[str, int] = {}
    for word in words(text):
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:n]  # repaired: a slice already stops before index n


def reading_time_minutes(text: str, words_per_minute: int = 200) -> int:
    """Whole minutes needed to read text, always rounded up.

    Any text at all takes at least one minute; empty text takes none. The
    reading speed must be a positive number of words per minute.

        reading_time_minutes("hello there")            -> 1
        reading_time_minutes("word " * 500)            -> 3
        reading_time_minutes("word " * 500, 100)       -> 5
        reading_time_minutes("")                       -> 0
    """
    if words_per_minute <= 0:
        raise ValueError(f"words_per_minute must be positive, got {words_per_minute}")
    return math.ceil(word_count(text) / words_per_minute)
