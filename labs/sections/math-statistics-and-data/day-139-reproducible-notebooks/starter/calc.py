"""The one piece of logic in this lab that lives in a module, not a cell.

Day 139's rule: exploration belongs in the notebook, but anything the
rest of a project depends on belongs in an imported module that has its
own tests -- the notebook then becomes a caller, not the only place the
logic exists. This module is that split made concrete: ``clean_mean`` is
plain, reusable, deterministic logic, and ``test_calc.py`` tests it the
ordinary way, with no kernel and no notebook involved.
"""

from __future__ import annotations


def clean_mean(values: list) -> float:
    """Mean of ``values`` after dropping ``None`` entries.

    Raises ``ValueError`` if every value is ``None`` or the list is empty,
    because a mean of nothing is not a number this function will guess at.
    """
    kept = [v for v in values if v is not None]
    if not kept:
        raise ValueError("clean_mean: no non-None values to average")
    return sum(kept) / len(kept)
