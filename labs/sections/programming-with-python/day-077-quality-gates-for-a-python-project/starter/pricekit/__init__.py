"""pricekit — a very small pricing library, used here as a subject for a quality gate.

The package is deliberately tiny. The interesting artefact in this lab is not
the library; it is `check.sh`, the single command that decides whether a change
to this library is safe to merge.
"""

from pricekit.money import CurrencyMismatch, InvalidMoney, Money, MoneyError
from pricekit.receipt import (
    apply_discount,
    format_receipt,
    line_total,
    subtotal,
    with_tax,
)

__all__ = [
    "CurrencyMismatch",
    "InvalidMoney",
    "Money",
    "MoneyError",
    "apply_discount",
    "format_receipt",
    "line_total",
    "subtotal",
    "with_tax",
]
