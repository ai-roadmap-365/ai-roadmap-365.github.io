"""Price a small shop receipt.

This is the same module as `examples/messy/receipts.py`, after the tools
and one human decision have been through it. Compare the two files side by
side with `diff -u ../messy/receipts.py receipts.py`.

Almost every difference was made mechanically: `ruff check --fix` removed
the two unused imports and the unread local, `ruff check --fix
--unsafe-fixes` rewrote the two `== None` comparisons, collapsed the
if/else into a ternary and replaced the mutable default, and `ruff format`
re-quoted, re-spaced and re-wrapped everything. Only the percent-format
strings at the end were rewritten by hand, because the nested formatting
was beyond what the fix could see.

The behaviour is byte-for-byte identical to the messy version, with one
deliberate exception: `add_item` no longer shares a default basket between
calls. That was a real bug, `B006` found it, and fixing it is a decision a
person has to make and a test has to record.
"""

import re
from decimal import Decimal

TAX_RATE = Decimal("0.20")
LINE_PATTERN = re.compile(r"^(.+?)\s+([0-9]+)$")


def add_item(name, price_cents, basket=None):
    if basket is None:
        basket = []
    basket.append({"name": name, "price_cents": price_cents})
    return basket


def parse_line(line):
    match = LINE_PATTERN.match(line.strip())
    if match is None:
        return None
    return {"name": match.group(1), "price_cents": int(match.group(2))}


def load_basket(lines):
    basket = []
    for line in lines:
        item = parse_line(line)
        if item is None:
            continue
        add_item(item["name"], item["price_cents"], basket)
    return basket


def subtotal_cents(basket):
    total = 0
    for item in basket:
        total += item["price_cents"]
    return total


def tax_cents(basket):
    return int(Decimal(subtotal_cents(basket)) * TAX_RATE)


def total_cents(basket):
    return subtotal_cents(basket) + tax_cents(basket)


def describe(basket, name):
    hits = 0
    for item in basket:
        if item["name"] == name:
            hits += 1
    label = "found" if hits else "missing"
    return f"{name}: {label} x{hits}"


def format_receipt(basket, shop="Corner Shop"):
    rows = [shop]
    for item in basket:
        rows.append(f"{item['name']:<20}{item['price_cents'] / 100:>8.2f}")
    rows.append(f"{'TOTAL':<20}{total_cents(basket) / 100:>8.2f}")
    return "\n".join(rows)
