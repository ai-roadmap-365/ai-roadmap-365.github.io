"""Tests that live inside the documentation — `doctest`, also standard library.

Run it:

    python3 -m doctest -v examples/doctest_demo.py

`doctest` scans docstrings for lines beginning with the interactive prompt
`>>>`, runs them, and compares what comes back with the text on the following
line — character for character. The examples are documentation a reader trusts
*because* a machine checks them.

That character-for-character comparison is the whole story of doctest: it is
unbeatable for short, exact, illustrative results, and it is the wrong tool
the moment the result is long, unordered, or has a memory address in it.
"""


def initials(full_name: str) -> str:
    """Return the initials of a name, uppercased and dot-separated.

    >>> initials("ada lovelace")
    'A.L.'
    >>> initials("Grace Brewster Murray Hopper")
    'G.B.M.H.'
    >>> initials("   plato   ")
    'P.'
    >>> initials("")
    ''
    """
    parts = full_name.split()
    return "".join(part[0].upper() + "." for part in parts)


def truncate(text: str, limit: int) -> str:
    """Shorten text to at most `limit` characters, ending with a single dot.

    >>> truncate("hello", 10)
    'hello'
    >>> truncate("hello there friend", 8)
    'hello t.'
    >>> truncate("abc", 1)
    '.'

    Asking for a limit below one is a programming error, not a short string:

    >>> truncate("abc", 0)
    Traceback (most recent call last):
        ...
    ValueError: limit must be at least 1, got 0
    """
    if limit < 1:
        raise ValueError(f"limit must be at least 1, got {limit}")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "."


if __name__ == "__main__":
    import doctest

    failures, attempted = doctest.testmod(verbose=False)
    print(f"doctest: {attempted} examples attempted, {failures} failed")
    raise SystemExit(1 if failures else 0)
