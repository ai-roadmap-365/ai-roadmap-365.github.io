"""Tests for pricekit.receipt — Day 72's fixtures, Day 73's failing-test-first habit."""

import pytest

from pricekit.money import InvalidMoney, Money
from pricekit.receipt import (
    apply_discount,
    format_receipt,
    line_total,
    subtotal,
    with_tax,
)

Line = tuple[str, Money, int]


@pytest.fixture
def basket() -> list[Line]:
    """A three-line receipt whose arithmetic is easy to check by hand."""
    return [
        ("coffee", Money(450), 2),
        ("bread", Money(320), 1),
        ("olive oil", Money(1195), 3),
    ]


def test_line_total_multiplies_price_by_quantity() -> None:
    assert line_total(Money(450), 2) == Money(900)


def test_subtotal_of_an_empty_receipt_is_zero() -> None:
    assert subtotal([]) == Money(0)


def test_subtotal_adds_every_line(basket: list[Line]) -> None:
    # 900 + 320 + 3585 = 4805
    assert subtotal(basket) == Money(4805)


def test_subtotal_refuses_to_mix_currencies() -> None:
    mixed: list[Line] = [("a", Money(100, "EUR"), 1), ("b", Money(100, "USD"), 1)]
    with pytest.raises(Exception):
        subtotal(mixed)


@pytest.mark.parametrize(
    ("cents", "percent", "expected"),
    [
        (1000, 0, 1000),
        (1000, 10, 900),
        (1000, 100, 0),
        (999, 33, 670),  # 999 * 33 // 100 == 329, so 999 - 329 == 670
    ],
)
def test_apply_discount_rounds_the_discount_down(cents: int, percent: int, expected: int) -> None:
    assert apply_discount(Money(cents), percent) == Money(expected)


@pytest.mark.parametrize("percent", [-1, 101, 2.5, True])
def test_apply_discount_refuses_impossible_percentages(percent: object) -> None:
    with pytest.raises(InvalidMoney):
        apply_discount(Money(1000), percent)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("cents", "rate", "expected"),
    [
        (1000, 0, 1000),
        (1000, 21, 1210),
        (4805, 21, 5814),  # 4805 * 21 // 100 == 1009, so 4805 + 1009 == 5814
    ],
)
def test_with_tax_rounds_the_tax_down(cents: int, rate: int, expected: int) -> None:
    assert with_tax(Money(cents), rate) == Money(expected)


@pytest.mark.parametrize("rate", [-1, 2.5, True])
def test_with_tax_refuses_bad_rates(rate: object) -> None:
    with pytest.raises(InvalidMoney):
        with_tax(Money(1000), rate)  # type: ignore[arg-type]


def test_format_receipt_without_tax_omits_the_tax_line(basket: list[Line]) -> None:
    text = format_receipt(basket)
    assert "tax" not in text
    assert text.splitlines()[-1] == "total        48.05 EUR"


def test_format_receipt_with_tax_shows_every_line(basket: list[Line]) -> None:
    text = format_receipt(basket, tax_percent=21)
    lines = text.splitlines()
    assert len(lines) == 6
    assert lines[0] == "coffee         2 x 4.50 EUR = 9.00 EUR"
    assert lines[3] == "subtotal     48.05 EUR"
    assert lines[4] == "tax 21%      1009 cents"
    assert lines[5] == "total        58.14 EUR"
