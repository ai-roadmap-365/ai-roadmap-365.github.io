"""The library half of ``wordtally-tools``.

Three honest utilities over plain text. Nothing here touches the network, the
clock, or a random number, so every result below is reproducible.

Note the packaged data file: :func:`load_stopwords` reads
``wordtally/data/stopwords.txt`` through :mod:`importlib.resources` rather
than by building a path relative to ``__file__``. That matters for packaging.
A file only exists next to the module if the build actually put it in the
wheel, and ``importlib.resources`` is the supported way to ask for it whether
the package was installed from a wheel, installed editable, or is sitting in a
source tree.
"""

from __future__ import annotations

import re
from collections import Counter
from importlib import resources

__all__ = ["words", "count_words", "load_stopwords", "top_words"]

_WORD_RE = re.compile(r"[A-Za-z']+")


def words(text: str) -> list[str]:
    """Split ``text`` into lower-cased words.

    Apostrophes stay inside a word so ``don't`` counts once, not twice.
    """
    return [match.group(0).lower() for match in _WORD_RE.finditer(text)]


def count_words(text: str) -> int:
    """Return how many words ``text`` contains."""
    return len(words(text))


def load_stopwords() -> frozenset[str]:
    """Return the packaged stop-word list.

    Raises ``FileNotFoundError`` if the data file was not shipped with the
    package — which is exactly the failure a wheel built without
    ``package-data`` produces, and exactly why the lab checks for the file
    inside the built wheel.
    """
    data = resources.files("wordtally").joinpath("data/stopwords.txt")
    lines = data.read_text(encoding="utf-8").splitlines()
    return frozenset(line.strip().lower() for line in lines if line.strip())


def top_words(
    text: str,
    n: int = 3,
    *,
    skip_stopwords: bool = True,
) -> list[tuple[str, int]]:
    """Return the ``n`` most frequent words as ``(word, count)`` pairs.

    Ties are broken alphabetically so the result is deterministic. Raises
    ``ValueError`` when ``n`` is not positive.
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    found = words(text)
    if skip_stopwords:
        stopwords = load_stopwords()
        found = [word for word in found if word not in stopwords]
    counts = Counter(found)
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:n]
