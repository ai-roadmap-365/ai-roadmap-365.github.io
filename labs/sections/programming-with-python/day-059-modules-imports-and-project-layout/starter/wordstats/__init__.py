"""wordstats — the package you are building.

The mere presence of this ``__init__.py`` is what makes ``wordstats/`` an
importable package. It should also define the package's public API by
re-exporting the useful names from the submodules, so callers can write
``from wordstats import tokenize, top_n`` without knowing which file each lives
in. The reference is in ``examples/wordstats/__init__.py``.
"""
# Exercise 5: DEFINE THE PUBLIC API.
# Uncomment the two RELATIVE imports below (the leading dot means "this same
# package") so that `from wordstats import tokenize, count_words, top_n` works:
#
# from .tokens import tokenize
# from .stats import count_words, top_n

__version__ = "1.0.0"
__all__ = ["tokenize", "count_words", "top_n", "__version__"]
