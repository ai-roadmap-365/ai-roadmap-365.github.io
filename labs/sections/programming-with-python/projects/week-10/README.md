# Week 10 project — Expense Tracker

This week was about **files, errors, and object-oriented Python**: reading and
writing files safely, CSV and JSON in the real world, exception strategy,
classes and objects, inheritance versus composition and the dunder protocols,
dataclasses and type hints, and modelling a domain with objects. This project
is where those six days become one program: a **domain model** that owns its
rules, wrapped by adapters that talk to files and to a person at a terminal.

## What you are building

A **command-line expense tracker**. You import spending from a CSV export,
classify each expense into a category, and print a monthly summary report —
totals per category, the month's largest expenses, and how the month compares
with the one before it. The deck of skills on display is the point: money as a
value object that refuses to be wrong, expenses as entities with enforced
invariants, a repository that swaps CSV for JSON without touching the core, and
error handling that turns a bad row into a useful message instead of a
traceback.

## Requirements

Show this week's skills:

- **A domain model, not a bag of dicts** (Days 67, 70): `Money`, `Category`,
  `Expense`, and `Ledger` as real types. Nouns from the problem become classes;
  the rules live with the data they constrain.
- **Value objects as frozen dataclasses** (Days 69, 70): `Money` is immutable,
  compares by value, stores whole cents as an integer (never a float), and
  refuses to add two different currencies.
- **Invariants enforced at construction** (Days 66, 67): an expense amount is
  positive, its date is a real date, its category is one of a closed set — use
  `__post_init__` or the initializer, and raise a **domain exception**, not a
  bare `ValueError` from three layers down.
- **Composition over inheritance where it belongs** (Day 68): a `Ledger` *has*
  expenses. If you use inheritance, earn it — an abstract `Report` base with
  `MonthlyReport` and `CategoryReport` subclasses is the one place it fits.
- **Dunder protocols** (Day 68): `Ledger` supports `len()`, iteration, and `in`;
  `Money` implements `__add__`, `__eq__`, `__lt__`, and a `__repr__` you would
  be happy to see in a traceback.
- **CSV in, CSV and JSON out** (Days 64, 65): import with `csv.DictReader`,
  survive the messy realities (quoted commas, a BOM, a ragged row, a blank
  amount), and persist with an **atomic write** so an interrupted save cannot
  corrupt the store.
- **Errors that reach a human** (Day 66): bad rows are collected and reported
  with their line numbers; the program exits non-zero on a fatal problem and
  never prints a raw traceback at the CLI boundary.
- **A pure core** (Days 63, 70): totals, grouping, and comparison are computed
  by functions and methods that touch no files, so the tests need no fixtures on
  disk.

## Steps

1. Write the domain in plain sentences, underline the nouns and verbs, and
   classify entities versus value objects (Day 70). Keep the worksheet.
2. Name every invariant in one sentence each, and decide where each is enforced.
3. Build `Money` first and test it hard: addition, equality, ordering,
   immutability, currency mismatch, and cent-exact arithmetic.
4. Build `Category` as an `Enum` and `Expense` as a dataclass that validates in
   `__post_init__`.
5. Build `Ledger` with the container dunders plus `total()`, `by_category()`,
   and `month(year, month)`.
6. Write the CSV importer as an **adapter**: it converts rows into `Expense`
   objects or into a list of row errors, and it never touches report logic.
7. Write the repository: `save`/`load` to JSON via an atomic write, using
   `dataclasses.asdict` and a rebuild function.
8. Write the report layer and the argparse CLI: `import`, `report`, `export`.
9. Test the core with no files on disk, then test the adapters against the
   messy sample CSV.

## Expected output

- `expenses import data/january.csv` → reports how many rows were imported and
  lists any rejected rows with their line numbers and the reason.
- `expenses report --month 2026-01` → a per-category table with totals, the
  month's total, and the three largest expenses, with amounts printed to exactly
  two decimal places.
- `expenses report --month 2026-02 --compare` → the same table plus the change
  against January per category, with the direction of each change shown.
- `expenses export --json out/ledger.json` → a JSON file that reloads into an
  identical `Ledger` (round-trip equality asserted in the tests).
- `Money(1000, "USD") + Money(500, "EUR")` → a domain exception with a message
  naming both currencies, not a wrong number.
- A CSV row with a negative amount, a missing date, or an unknown category is
  rejected with its line number, and the remaining valid rows still import.

## Validation

- [ ] `Money` is a frozen dataclass storing integer cents; float arithmetic
      appears nowhere in the money path.
- [ ] Adding two currencies raises a domain exception; equality and ordering
      work by value, and `Money` is usable as a dict key.
- [ ] `Expense` rejects a non-positive amount, an unparseable date, and an
      unknown category, each with a clear domain exception.
- [ ] `Ledger` supports `len()`, iteration, and `in`, and its totals are exact
      to the cent.
- [ ] The core (money, expense, ledger, reports) is unit-tested with **no file
      access at all**.
- [ ] The CSV importer handles quoted commas, a BOM, a ragged row, and a blank
      amount, collecting errors rather than stopping at the first one.
- [ ] Saving uses a temp file plus `os.replace`, so an interrupted save leaves
      the previous store intact.
- [ ] JSON export reloads to an equal `Ledger` (round-trip test passes).
- [ ] The CLI prints human messages and exits non-zero on fatal errors; no raw
      traceback escapes to the terminal.
- [ ] Every public class and function has a docstring and type hints.

## Troubleshooting

- Totals off by a cent? You used floats. Store cents as an `int` and divide only
  when formatting for display.
- `FrozenInstanceError` while importing? A frozen dataclass cannot be mutated —
  build a new one with `dataclasses.replace` instead of assigning.
- `__hash__` suddenly gone? Defining `__eq__` on a normal class removes it. On a
  dataclass, `frozen=True` restores hashing; on a hand-written class, define
  `__hash__` yourself.
- BOM turning your first header into something unmatchable? Open the CSV with
  `encoding='utf-8-sig'` and compare the header names again.
- Blank rows or `None` amounts crashing the import? Validate the row *before*
  constructing the `Expense`, and record the failure with its line number from
  `reader.line_num`.
- Round-trip test failing on dates? Serialize with `date.isoformat()` and parse
  with `date.fromisoformat()` on the way back in — not `str()`.
- Report logic that needs a file to test? The reports belong in the core; pass a
  `Ledger` in, return numbers out, and keep printing in the CLI layer.
