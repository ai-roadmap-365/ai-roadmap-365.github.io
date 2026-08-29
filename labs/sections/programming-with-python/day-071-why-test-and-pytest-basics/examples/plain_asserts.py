"""A test suite with no test runner at all — just `assert`.

This is the whole idea of testing, stripped to the bone. Run it:

    python3 examples/plain_asserts.py

It prints nothing and exits 0 when everything holds. Break `textstats.py` and
it exits 1 with an AssertionError. That is already a test suite: arrange, act,
assert, and a process exit code a machine can read.

Then compare what it tells you on failure with what pytest tells you. That
difference — not the concept — is what you are paying pytest for.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from textstats import average_word_length, top_words, word_count, words  # noqa: E402

# --- words -----------------------------------------------------------------
assert words("The cat. The hat!") == ["the", "cat", "the", "hat"]
assert words("") == []

# --- word_count ------------------------------------------------------------
assert word_count("The cat. The hat!") == 4
assert word_count("") == 0

# --- average_word_length ---------------------------------------------------
assert average_word_length("the cat") == 3.0
assert average_word_length("") == 0.0

# --- top_words -------------------------------------------------------------
assert top_words("a b a c a b", 2) == [("a", 3), ("b", 2)]
assert top_words("a b a c a b", 0) == []

print("all plain assertions held")
