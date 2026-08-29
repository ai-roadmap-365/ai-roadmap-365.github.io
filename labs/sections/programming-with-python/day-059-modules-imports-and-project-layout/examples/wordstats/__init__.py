"""wordstats — a tiny, multi-module package that counts word frequencies.

This file, ``__init__.py``, is what turns the ``wordstats/`` directory into a
*package*: an importable name that groups several modules. It also defines the
package's public API by re-exporting the useful names from the submodules, so
a caller can write::

    from wordstats import tokenize, top_n

without needing to know that ``tokenize`` lives in ``tokens.py`` and ``top_n``
lives in ``stats.py``. The two imports below are *relative* imports (the
leading dot means "from this same package"), which is the normal way one part
of a package refers to another.
"""
from .tokens import tokenize
from .stats import count_words, top_n

__version__ = "1.0.0"
__all__ = ["tokenize", "count_words", "top_n", "__version__"]
