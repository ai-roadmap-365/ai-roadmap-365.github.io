# Day 067 lab — Building Your First Classes

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Classes and Objects
- **Day number:** 67 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-067-classes-and-objects
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-067-classes-and-objects` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 67 is where a dict stops being enough. You have been modelling things
as a dict plus a pile of functions that all take that dict as their first
argument, and that works right up until someone reaches in and writes
`account["balance"] = -500`, walking past every rule those functions were
written to enforce.

In this lab you take exactly that program — `examples/account_dict.py`, an
account as a dict with `make_account`, `deposit`, `withdraw`, and
`describe` — and convert it into a class, then prove with a test that the
behaviour did not change. Along the way you reproduce the classic shared
mutable class attribute bug and fix it, add a `__repr__` and see the
before-and-after, add a `@property` that rejects an invalid value, add a
`@classmethod` alternative constructor that builds an instance from a CSV
row (straight from Day 65), and finally open the hood with `vars()`,
`type()`, and `__dict__` to see that a class really is a dict of state plus
a dict of functions with syntax on top.

## Learning objectives

- Convert a dict-plus-functions program into a class, and demonstrate with
  a test that the behaviour is identical.
- Explain what `self` is, who supplies it, and how `obj.method(x)` becomes
  `Class.method(obj, x)`.
- Distinguish an instance attribute from a class attribute, reproduce the
  shared mutable class attribute bug, and fix it in `__init__`.
- Write a `__repr__` that makes an object useful in the REPL, a traceback,
  and a debugger.
- Use `@property` to validate an attribute on assignment, and catch the
  exception it raises.
- Use `@classmethod` as an alternative constructor and `@staticmethod` for
  a rule that needs neither the instance nor the class.
- Inspect the machinery with `type()`, `vars()`, and `__dict__` and say
  where state lives and where behaviour lives.

## Prerequisites

- The Day 67 lesson (read it first — it walks this exact class end to end).
- Day 65: CSV as text, which is what `from_csv_row` parses.
- Day 66: exceptions — `raise`, `try`/`except`, and choosing `ValueError`.
- Days 53, 57, 58: dictionaries in depth, functions, and closures (the
  from-scratch object system in `examples/closure_object.py` uses closures).
- A text editor and a terminal. Nothing beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (authored and executed on macOS, Apple
  Silicon, Python 3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. Everything here is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The scripts build a handful of small
objects in memory and print a few dozen lines; no special memory, disk, or
GPU is needed.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — no packages to install. See
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. Classes are part of the language itself, so there is nothing to
buy, install, or sign up for. No account, API key, or network access is
needed at any point.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-067-classes-and-objects
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-067-classes-and-objects/
├── README.md                    ← you are here
├── metadata.yml                 ← machine-readable lab metadata
├── starter/
│   ├── account.py               ← YOUR working file (5 numbered exercises)
│   └── inspection-notes.md      ← exercise 6: record what the machinery shows
├── examples/
│   ├── account_dict.py          ← the "before": a dict + loose functions
│   ├── account.py               ← the "after": the reference Account class
│   ├── shared_bug.py            ← the shared mutable class attribute, and its fix
│   ├── compare.py               ← proves the two versions behave identically
│   ├── closure_object.py        ← an object built from dicts + closures, no `class`
│   ├── machinery.py             ← type(), vars(), __dict__, bound methods, mangling
│   └── accounts.csv             ← four rows for the classmethod constructor
├── tests/
│   └── run_tests.sh             ← behaviour checks for the reference and your starter
├── expected-output/
│   ├── sample-run.txt           ← real captured run of every example script
│   ├── test-run.txt             ← real captured run of the test suite
│   └── FIELDS.md                ← required behaviour on every platform
├── requirements/
│   └── README.md                ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory, in order:

```bash
# 1. See the "before": a dict plus functions. Watch the last line —
#    a direct edit walks straight past every rule the functions enforce.
python3 examples/account_dict.py

# 2. See the "after": the same program as a class, refusing that same edit.
python3 examples/account.py

# 3. Prove the conversion changed nothing: same moves, same results,
#    then a whole CSV file loaded through the classmethod constructor.
python3 examples/compare.py

# 4. Reproduce the classic bug: one list on the class, shared by everybody.
python3 examples/shared_bug.py

# 5. Build an object from scratch with dicts and closures, and compare it
#    to the same thing written with `class`.
python3 examples/closure_object.py

# 6. Open the hood: type(), vars(), __dict__, bound methods, name mangling.
python3 examples/machinery.py

# 7. Your task: work through the five numbered exercises in
#    starter/account.py, running it as you go.
python3 starter/account.py

# 8. Exercise 6: run the one-liners in starter/inspection-notes.md against
#    your own class and fill in what you saw.

# 9. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/account_dict.py` — runs the dict version through a
  deposit, a withdrawal, a refused overdraft, and then a direct
  `account["balance"] = -500`, which succeeds. That success is the problem
  this lab solves.
- `python3 examples/account.py` — runs the class version through the same
  session. The overdraft is refused for the same reason as before, but the
  negative-balance assignment is now refused too, by the `@property` setter.
- `python3 examples/compare.py` — drives both versions through an identical
  list of moves and compares the resulting descriptions and histories, which
  is what "the refactor changed nothing" actually means. It then reads
  `examples/accounts.csv` and builds four accounts with
  `Account.from_csv_row`.
- `python3 examples/shared_bug.py` — creates two `BuggyAccount` instances
  whose `history` is a class-level list, shows one instance's deposit
  appearing in the other's history, and then shows the fixed class where the
  list is created inside `__init__`.
- `python3 examples/closure_object.py` — builds an account with nothing but
  a dict and closures (no `class` keyword anywhere), then the same account
  with `class`, and prints where each keeps its state and its functions.
- `python3 examples/machinery.py` — prints `type()` of an instance and of
  the class, `vars()` of two instances so you can see their separate state,
  the class dictionary so you can see where the methods live, the bound
  method's `__self__` and `__func__`, an unsugared `Account.deposit(ada, 10)`
  call, and how `__pin` becomes `_Card__pin`.
- `python3 starter/account.py` — runs your work in progress. Until you finish
  the exercises it raises `NotImplementedError`, which is deliberate.
- `bash tests/run_tests.sh` — checks real behaviour: separate per-instance
  state, a defended invariant, a rejecting property, an exact `__repr__`
  string, a working classmethod and staticmethod, the bound-method
  mechanism, and an assertion that the class and dict versions produce
  identical results. Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run of every example script. The heart of it is these two
sessions, side by side:

```text
$ python3 examples/account_dict.py
ada: 120.00 (2 entries)
rejected: insufficient funds
after a direct edit: ada: -500.00 (2 entries)

$ python3 examples/account.py
ada: 120.00 (2 entries)
rejected: insufficient funds
rejected: balance cannot be negative (got -500.00)
after the refused edit: ada: 120.00 (2 entries)
repr: Account(owner='ada', balance=120.00)
```

and this, from the shared-attribute bug:

```text
$ python3 examples/shared_bug.py
--- buggy: one list shared by every instance ---
ada.history: [('ada', 10), ('bob', 20)]
bob.history: [('ada', 10), ('bob', 20)]
same list object? True
```

Everything is deterministic, so your output will match — with one honest
exception documented in
[`expected-output/FIELDS.md`](expected-output/FIELDS.md): an object printed
without a custom `__repr__` shows a memory address that differs on every
run. No captured output and no test in this lab depends on one.

## Validation steps

1. `python3 examples/account_dict.py` ends with
   `after a direct edit: ada: -500.00 (2 entries)`.
2. `python3 examples/account.py` ends with
   `repr: Account(owner='ada', balance=120.00)` and never shows a negative
   balance.
3. `python3 examples/compare.py` prints `descriptions identical: True`,
   `histories identical:    True`, and `loaded 4 accounts, total 2225.75 USD`.
4. `python3 examples/shared_bug.py` prints `same list object? True` for the
   buggy class and `same list object? False` for the fixed one.
5. `python3 examples/closure_object.py` prints `outputs identical: True`.
6. `python3 examples/machinery.py` prints `ada.deposit.__self__ is ada: True`
   and `hasattr(card, '_Card__pin'): True`.
7. Your `starter/account.py` runs without `NotImplementedError` and prints
   the same description, repr, rejection, and CSV-built account as the
   reference.
8. `starter/inspection-notes.md` has every "What I saw" cell filled in from
   your own runs.
9. `bash tests/run_tests.sh` ends with `0 failure(s)` and exits `0`.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `28 checks, 0
failure(s).` Once all five starter exercises are complete, the suite stops
checking structure and runs your class through the same twelve behaviour
checks as the reference, giving `34 checks, 0 failure(s).` The command exits
0 on success and non-zero on any failure, so it can run unattended. A full
captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

Nothing to clean up: the scripts write no files and create no temporary
directories. To reset your work, restore the starter from git:

```bash
git checkout -- starter/account.py starter/inspection-notes.md
```

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the `__init__` argument-count error, `AttributeError` for an
attribute you never assigned, the infinite recursion you get when a property
setter assigns to its own name, a setter that never runs, one account's
deposit landing in another's history, `ModuleNotFoundError` for `account`,
the default `<... object at 0x...>` repr, and the classmethod signature.

## Security notes

See [security.md](security.md). Short version: no network, no privileges,
no installs, no files written. The lab's security-relevant idea is that a
class is an enforcement point — the rules that keep data valid live with the
data, in one auditable place — plus two cautions: Python's underscore
conventions are conventions, not walls (name mangling turns `__pin` into a
visible `_Card__pin`), and `__repr__` output ends up in logs and tracebacks,
so keep secrets out of it.

## Extension exercises

1. Add a `transfer(self, other, amount)` method that moves money from this
   account to another `Account`. Decide first what the invariant is when
   two objects are involved, and make sure a failed transfer leaves *both*
   balances unchanged.
2. Add a read-only `@property` called `movements` that returns
   `len(self.history)` and has no setter, then confirm that assigning to it
   raises `AttributeError`. That is how you express "computed, and not
   yours to set."
3. Add a class attribute `accounts_opened` and increment it in `__init__`
   (the reference class in `examples/account.py` does this — read how).
   Then explain in one sentence why `self.accounts_opened += 1` would
   silently create a per-instance attribute instead of updating the shared
   counter.
4. Write `to_csv_row(self)` as the mirror of `from_csv_row`, and prove the
   round trip: `Account.from_csv_row(a.to_csv_row())` produces an account
   with the same owner and balance.
5. Rewrite `examples/closure_object.py`'s `make_account` so the returned
   dict also carries a `history` accessor, then write down which parts of
   the class machinery you had to hand-build — and which ones you got for
   free from `class`.

## Navigation

- **Previous day:** Day 66 — Exceptions and Error Handling Strategy
  (`labs/sections/programming-with-python/day-066-exceptions-and-error-handling-strategy/`).
- **Next day:** Day 68 — Inheritance, Composition, and Dunder Methods
  (`labs/sections/programming-with-python/day-068-inheritance-composition-and-dunder-methods/`),
  which takes the class you built here and teaches it to cooperate with
  other classes and with Python's own operators.
- **Week 10 project:** the Expense Tracker — CSV import and export, category
  classes, and monthly summary reports. The `from_csv_row` classmethod and
  the validating property you write today are exactly the pieces that
  project is built from.
