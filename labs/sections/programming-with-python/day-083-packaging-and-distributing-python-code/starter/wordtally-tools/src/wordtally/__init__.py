"""wordtally — count and rank the words in a text file.

The import name is ``wordtally``. The distribution name — what you type after
``pip install`` — is ``wordtally-tools``. They differ deliberately, because in
the real world they differ constantly: ``pip install beautifulsoup4`` gives
you ``import bs4``, which you met on Day 79.

The version is single-sourced. It is written once, in ``pyproject.toml``, and
read back here from the installed metadata. There is no second copy to forget
to update.
"""

from importlib.metadata import PackageNotFoundError, version

from wordtally.core import count_words, load_stopwords, top_words, words

try:
    __version__ = version("wordtally-tools")
except PackageNotFoundError:  # running from a source tree, never installed
    __version__ = "0.0.0.dev0"

__all__ = [
    "__version__",
    "count_words",
    "load_stopwords",
    "top_words",
    "words",
]
