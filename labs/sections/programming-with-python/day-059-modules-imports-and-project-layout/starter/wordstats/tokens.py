"""tokens.py — one responsibility: turn raw text into a clean list of words.

This module should import only the standard library and must NOT import its
sibling ``stats`` — keeping the dependency one-directional is how you avoid
circular imports. The finished reference is in
``examples/wordstats/tokens.py`` — try each exercise before peeking.
"""
import re

# Matches runs of letters, digits, and apostrophes, so "don't" stays one word.
_WORD_RE = re.compile(r"[a-z0-9']+")


def normalize(text):
    """Return text lowercased — a tiny, separately testable step. (Provided.)"""
    return text.lower()


def tokenize(text):
    """Split text into a list of lowercase word tokens."""
    # Exercise 1: TOKENIZE.
    # Return a list of lowercase word tokens found in text. Lowercase first
    # with normalize(text), then use _WORD_RE.findall(...) on the result.
    # tokenize("Hello, HELLO world!") must return ['hello', 'hello', 'world'].
    raise NotImplementedError("Exercise 1: implement tokenize")
