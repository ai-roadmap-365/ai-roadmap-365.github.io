"""Tests for pricekit.money — Day 71's arrange/act/assert, Day 72's parametrize."""

import pytest

from pricekit.money import CurrencyMismatch, InvalidMoney, Money


def test_money_adds_within_a_currency() -> None:
    assert Money(2900) + Money(4900) == Money(7800)


def test_money_refuses_to_mix_currencies() -> None:
    with pytest.raises(CurrencyMismatch):
        Money(100, "EUR") + Money(100, "USD")


@pytest.mark.parametrize(
    "cents",
    [-1, -95000],
)
def test_money_refuses_negative_amounts(cents: int) -> None:
    with pytest.raises(InvalidMoney):
        Money(cents)


@pytest.mark.parametrize(
    "cents",
    [1.5, "4215", True, None],
)
def test_money_refuses_amounts_that_are_not_whole_cents(cents: object) -> None:
    with pytest.raises(InvalidMoney):
        Money(cents)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "currency",
    ["eur", "EURO", "E", ""],
)
def test_money_refuses_bad_currency_codes(currency: str) -> None:
    with pytest.raises(InvalidMoney):
        Money(100, currency)


def test_times_repeats_an_amount() -> None:
    assert Money(1250).times(3) == Money(3750)


def test_times_by_zero_is_zero() -> None:
    assert Money(1250).times(0) == Money(0)


@pytest.mark.parametrize(
    "quantity",
    [-1, 2.5, True],
)
def test_times_refuses_bad_quantities(quantity: object) -> None:
    with pytest.raises(InvalidMoney):
        Money(1250).times(quantity)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("cents", "text"),
    [
        (0, "0.00 EUR"),
        (7, "0.07 EUR"),
        (1250, "12.50 EUR"),
        (95000, "950.00 EUR"),
    ],
)
def test_str_formats_cents_as_a_decimal_amount(cents: int, text: str) -> None:
    assert str(Money(cents)) == text


def test_money_is_frozen() -> None:
    amount = Money(1250)
    with pytest.raises(Exception):
        amount.cents = 99  # type: ignore[misc]
