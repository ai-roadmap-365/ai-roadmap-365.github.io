"""Receipt arithmetic built on top of `Money`.

Every function here is pure: values in, values out, no files and no printing.
That is what lets the whole module be measured, typed and tested by a gate
that finishes in under a second.
"""

from __future__ import annotations

from collections.abc import Sequence

from pricekit.money import InvalidMoney, Money


def line_total(unit_price: Money, quantity: int) -> Money:
    """Return the cost of `quantity` items at `unit_price`."""
    return unit_price.times(quantity)


def subtotal(lines: Sequence[tuple[str, Money, int]]) -> Money:
    """Sum every line of a receipt.

    Each line is a (description, unit price, quantity) triple. An empty
    receipt totals zero in EUR, because there is no currency to infer.
    """
    if not lines:
        return Money(0)
    total = line_total(lines[0][1], lines[0][2])
    for _, unit_price, quantity in lines[1:]:
        total = total + line_total(unit_price, quantity)
    return total


def apply_discount(amount: Money, percent: int) -> Money:
    """Reduce `amount` by `percent`, rounding the discount down to a whole cent."""
    if isinstance(percent, bool) or not isinstance(percent, int):
        raise InvalidMoney(f"percent must be a whole number, got {percent!r}")
    if percent < 0 or percent > 100:
        raise InvalidMoney(f"percent must be between 0 and 100, got {percent}")
    discount = amount.cents * percent // 100
    return Money(amount.cents - discount, amount.currency)


def with_tax(amount: Money, rate_percent: int) -> Money:
    """Add `rate_percent` tax to `amount`, rounding the tax down to a whole cent."""
    if isinstance(rate_percent, bool) or not isinstance(rate_percent, int):
        raise InvalidMoney(f"rate must be a whole number, got {rate_percent!r}")
    if rate_percent < 0:
        raise InvalidMoney(f"rate cannot be negative, got {rate_percent}")
    tax = amount.cents * rate_percent // 100
    return Money(amount.cents + tax, amount.currency)


def format_receipt(lines: Sequence[tuple[str, Money, int]], tax_percent: int = 0) -> str:
    """Render a receipt as plain text, one line per item plus a total."""
    rendered = [
        f"{description:<12} {quantity:>3} x {unit_price} = {line_total(unit_price, quantity)}"
        for description, unit_price, quantity in lines
    ]
    net = subtotal(lines)
    gross = with_tax(net, tax_percent)
    rendered.append(f"{'subtotal':<12} {net}")
    if tax_percent:
        rendered.append(f"{'tax ' + str(tax_percent) + '%':<12} {gross.cents - net.cents} cents")
    rendered.append(f"{'total':<12} {gross}")
    return "\n".join(rendered)
