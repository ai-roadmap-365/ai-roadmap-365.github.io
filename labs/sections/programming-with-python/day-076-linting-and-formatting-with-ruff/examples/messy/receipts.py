"""Price a small shop receipt.

This module WORKS. Every function does what its name says, and the test
suite next door passes. It is also written badly on purpose: unsorted
imports, an import nobody uses, a local variable nobody reads, a line far
too long, two comparisons to None written the wrong way, string formatting
from an older era of Python, and one mutable default argument that is a
genuine bug rather than a cosmetic complaint.

Nothing here is exaggerated. Every one of these appears in real code
written by people in a hurry.
"""
import json
from collections import Counter
import re
from decimal import Decimal

TAX_RATE = Decimal('0.20')
LINE_PATTERN = re.compile(r'^(.+?)\s+([0-9]+)$')


def add_item(name, price_cents, basket = []):
    basket.append({'name': name, 'price_cents': price_cents})
    return basket


def parse_line(line):
    match = LINE_PATTERN.match(line.strip())
    if match == None:
        return None
    return {'name': match.group(1), 'price_cents': int(match.group(2))}


def load_basket(lines):
    basket = []
    skipped = 0
    for line in lines:
        item = parse_line(line)
        if item == None:
            continue
        add_item(item['name'], item['price_cents'], basket)
    return basket


def subtotal_cents(basket):
    total = 0
    for item in basket:
        total += item['price_cents']
    return total


def tax_cents(basket):
    return int(Decimal(subtotal_cents(basket)) * TAX_RATE)


def total_cents(basket):
    return subtotal_cents(basket) + tax_cents(basket)


def describe(basket, name):
    hits = 0
    for item in basket:
        if item['name'] == name:
            hits += 1
    if hits:
        label = 'found'
    else:
        label = 'missing'
    return '%s: %s x%d' % (name, label, hits)


def format_receipt(basket, shop = 'Corner Shop'):
    rows = [shop]
    for item in basket:
        rows.append('{:<20}{:>8}'.format(item['name'], '%.2f' % (item['price_cents'] / 100)))
    rows.append('{:<20}{:>8}'.format('TOTAL', '%.2f' % (total_cents(basket) / 100)))
    return '\n'.join(rows)
