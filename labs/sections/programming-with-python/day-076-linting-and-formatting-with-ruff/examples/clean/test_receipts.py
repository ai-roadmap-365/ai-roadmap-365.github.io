"""Behaviour tests for the cleaned receipts module.

Every test below is character-for-character the same as the one in
`examples/messy/test_receipts.py`, except the last one. That is the whole
argument of this lab: the formatter and the linter rewrote the module
substantially and not one assertion about its behaviour had to change.

The last test changed because a person changed the behaviour on purpose,
after `B006` pointed at the bug.
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


def test_default_basket_is_fresh_on_every_call():
    """The fixed version of the B006 test.

    Two calls that omit `basket` must get two independent baskets. In the
    messy version they got the same one, and `first is second` was true.
    """
    first = receipts.add_item("apple", 120)
    second = receipts.add_item("pear", 95)
    assert first is not second
    assert first == [{"name": "apple", "price_cents": 120}]
    assert second == [{"name": "pear", "price_cents": 95}]
