"""tokens.py — one responsibility: turn raw text into a clean list of words.

This module knows nothing about counting, reporting, or the command line. It
imports only the standard library and never imports its sibling ``stats`` — a
module that does one job and does not depend on the rest of the package is the
easiest to test and the least likely to cause a circular import.
"""
import re

# Matches runs of letters, digits, and apostrophes, so "don't" stays one word.
_WORD_RE = re.compile(r"[a-z0-9']+")


def normalize(text):
    """Return text lowercased — a tiny, separately testable step."""
    return text.lower()


def tokenize(text):
    """Split text into a list of lowercase word tokens.

    Punctuation and whitespace act as separators; internal apostrophes are
    kept. ``tokenize("Hello, HELLO world!")`` returns
    ``['hello', 'hello', 'world']``.
    """
    return _WORD_RE.findall(normalize(text))
