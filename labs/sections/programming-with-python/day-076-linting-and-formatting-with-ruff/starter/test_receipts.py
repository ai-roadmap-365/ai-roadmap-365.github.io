"""Behaviour tests for the messy receipts module.

These tests exist to PIN CURRENT BEHAVIOUR. Their whole job is to be green
before you touch the file and green after the formatter and the linter have
rewritten it, so that you can see with your own eyes that neither tool
changed what the code does.

One test below deliberately asserts a bug. It is labelled.
"""

import receipts


def test_parse_line_reads_a_name_and_a_price():
    assert receipts.parse_line("apple 120") == {"name": "apple", "price_cents": 120}


def test_parse_line_keeps_multi_word_names():
    assert receipts.parse_line("brown bread 240") == {
        "name": "brown bread",
        "price_cents": 240,
    }


def test_parse_line_returns_none_for_junk():
    assert receipts.parse_line("nonsense") is None
    assert receipts.parse_line("") is None


def test_load_basket_skips_unparseable_lines():
    basket = receipts.load_basket(["apple 120", "nonsense", "pear 95"])
    assert [item["name"] for item in basket] == ["apple", "pear"]


def test_subtotal_adds_every_price():
    basket = receipts.load_basket(["apple 120", "pear 95"])
    assert receipts.subtotal_cents(basket) == 215


def test_tax_is_twenty_percent_of_the_subtotal():
    basket = receipts.load_basket(["apple 120", "pear 95"])
    assert receipts.tax_cents(basket) == 43


def test_total_is_subtotal_plus_tax():
    basket = receipts.load_basket(["apple 120", "pear 95"])
    assert receipts.total_cents(basket) == 258


def test_describe_counts_matching_items():
    basket = receipts.load_basket(["apple 120", "apple 130", "pear 95"])
    assert receipts.describe(basket, "apple") == "apple: found x2"
    assert receipts.describe(basket, "plum") == "plum: missing x0"


def test_format_receipt_has_a_header_and_a_total_row():
    basket = receipts.load_basket(["apple 120", "pear 95"])
    rows = receipts.format_receipt(basket).splitlines()
    assert rows[0] == "Corner Shop"
    assert rows[-1] == "TOTAL                   2.58"
    assert len(rows) == 4


def test_default_basket_is_shared_between_calls():
    """THIS TEST DOCUMENTS A BUG, NOT A FEATURE.

    `add_item`'s default `basket = []` is one list, created once when the
    `def` line ran. Every call that omits `basket` appends to that same
    list, so two unrelated shoppers end up sharing a trolley. The linter
    rule B006 flags exactly this. Exercise 6 fixes it, and this test is
    then rewritten to assert the correct behaviour instead.
    """
    first = receipts.add_item("apple", 120)
    second = receipts.add_item("pear", 95)
    assert first is second
    assert [item["name"] for item in second][-2:] == ["apple", "pear"]
