"""Whole-cent money arithmetic.

Money is stored as an integer number of cents plus a three-letter currency
code, for the reason Day 70 argued: integer addition is exact, so a total can
never depend on which particular amounts a user happened to enter.
"""

from __future__ import annotations

from dataclasses import dataclass


class MoneyError(Exception):
    """Base class for every rule this module refuses to break."""


class InvalidMoney(MoneyError):
    """A money value that cannot exist."""


class CurrencyMismatch(MoneyError):
    """An operation that mixes two currencies."""


@dataclass(frozen=True)
class Money:
    """An exact amount of money: whole cents in one currency."""

    cents: int
    currency: str = "EUR"

    def __post_init__(self) -> None:
        if isinstance(self.cents, bool) or not isinstance(self.cents, int):
            raise InvalidMoney(f"money is whole cents, got {self.cents!r}")
        if self.cents < 0:
            raise InvalidMoney(f"money cannot be negative, got {self.cents}")
        if len(self.currency) != 3 or not self.currency.isupper():
            raise InvalidMoney(f"currency must be a code like EUR, got {self.currency!r}")

    def __add__(self, other: Money) -> Money:
        if other.currency != self.currency:
            raise CurrencyMismatch(f"cannot add {other.currency} to {self.currency}")
        return Money(self.cents + other.cents, self.currency)

    def times(self, quantity: int) -> Money:
        """Return this amount repeated `quantity` times."""
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise InvalidMoney(f"quantity must be a whole number, got {quantity!r}")
        if quantity < 0:
            raise InvalidMoney(f"quantity cannot be negative, got {quantity}")
        return Money(self.cents * quantity, self.currency)

    def __str__(self) -> str:
        return f"{self.cents // 100}.{self.cents % 100:02d} {self.currency}"
