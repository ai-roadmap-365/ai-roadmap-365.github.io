"""Exercise 7 — watch `Any` switch the checker off.

Run mypy on this file as it stands:

    python3 -m mypy starter/any_demo.py

You get one error, with the code [union-attr]: `lookup` may return None, and
`shout` calls .upper() on the result without checking.

Now change ONE character sequence. Replace the return annotation of `lookup`

    def lookup(name: str) -> str | None:

with

    def lookup(name: str) -> Any:

and run mypy again. The error is gone. Nothing about the code got safer —
`lookup` still returns None for an unknown name, and `shout` will still raise
AttributeError at runtime. All that changed is that you told the checker to
stop looking.

That is what `Any` means: not "some type", but "stop checking here". Every
Any you write is a hole, and the hole is not local — it spreads to every
value that flows out of it.

Change it back when you are done.
"""

from typing import Any

WORDS: dict[str, str] = {"a": "alpha", "b": "bravo"}

# `Any` is imported ready for the exercise; it is unused until you make the
# edit described above. mypy does not complain about unused imports — that is
# a linter's job, and it is tomorrow's lesson.


def lookup(name: str) -> str | None:
    """Return the word for a letter, or None when the letter is unknown."""
    return WORDS.get(name)


def shout(name: str) -> str:
    """Upper-case the word for a letter."""
    return lookup(name).upper()
