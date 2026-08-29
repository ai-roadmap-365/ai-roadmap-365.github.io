"""The most important test file in this lab, because it is worthless.

Every function below is CALLED. Not one of them is CHECKED. There is not a
single `assert` in this file, so it cannot fail for any reason other than an
unhandled exception — and yet coverage.py will report a very high number for
`pricekit.receipt`, because coverage measures which lines RAN, never whether
anything about the result was true.

Run it and read the report:

    coverage run --branch --source=pricekit -m pytest coverage-demo -q
    coverage report --show-missing --fail-under=0

That is the whole argument against coverage as a target, in one file.
"""

from pricekit.money import Money
from pricekit.receipt import apply_discount, format_receipt, line_total, subtotal, with_tax

BASKET = [
    ("coffee", Money(450), 2),
    ("bread", Money(320), 1),
    ("olive oil", Money(1195), 3),
]


def test_line_total_runs() -> None:
    line_total(Money(450), 2)


def test_subtotal_runs() -> None:
    subtotal(BASKET)
    subtotal([])


def test_apply_discount_runs() -> None:
    apply_discount(Money(1000), 10)


def test_with_tax_runs() -> None:
    with_tax(Money(1000), 21)
    with_tax(Money(1000), 0)


def test_format_receipt_runs() -> None:
    format_receipt(BASKET)
    format_receipt(BASKET, tax_percent=21)
