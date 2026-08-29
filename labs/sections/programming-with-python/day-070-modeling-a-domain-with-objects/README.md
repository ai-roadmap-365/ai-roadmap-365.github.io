# Day 070 lab — Modelling Northside Gym

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Modeling a Domain with Objects
- **Day number:** 70 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-070-modeling-a-domain-with-objects
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-070-modeling-a-domain-with-objects` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 70 is the day the week's parts become a method. This lab hands you what a
real modelling job actually starts with: a page of plain-English rules from a
gym owner — eleven numbered sentences and a short vocabulary list — and
nothing else. No schema, no class diagram, no starter hints about which noun
becomes which type.

Your job is to turn those sentences into a **domain model**: value objects
that cannot hold an invalid value, entities identified by something that never
changes, invariants enforced at the exact moment an object is built, a pure
core that touches no file, a repository that hides JSON behind two methods,
and a domain exception family the command-line adapter can translate into
sentences a person can act on.

The domain is deliberately *not* the spending tracker from the lesson. The
lesson models expenses because that is what the Week 10 project asks for; the
lab models gym membership so that you practise the method on something new
rather than copying an answer you have already seen. The two share not one
line of code — only the discipline.

The design is what is being tested here, not just the functions. The suite
proves your value objects are frozen, your entities compare by identity, every
refusal belongs to one exception family, the round trip through JSON loses
nothing, and — twice over, once by reading your imports and once by running
your core from an empty directory — that the core genuinely cannot touch the
outside world.

## Learning objectives

- Extract nouns and verbs from stated domain rules and decide which class owns
  each behaviour, before writing any code.
- Classify each noun as an entity (identity, a life cycle) or a value object
  (defined entirely by its values, immutable) and justify each choice in one
  sentence.
- Implement value objects as frozen dataclasses that validate in
  `__post_init__` and refuse invalid values — a malformed membership number, a
  negative price, a mismatched currency, a backwards billing period.
- Implement an entity whose equality and hash come from its identity, so it
  stays the same member after a rename, a plan switch and fifty check-ins.
- Enforce a rule that spans two objects (the monthly check-in limit, the
  duplicate-number refusal) in the object that can see enough to check it.
- Keep a domain core free of input and output, and demonstrate the payoff by
  testing every rule from an empty directory.
- Put every storage decision in one repository class, and rebuild loaded
  values through the domain constructors so a hand-edited file is refused.
- Fill in an anti-pattern checklist against your own design — god object,
  anemic model, primitive obsession, premature inheritance, stringly typed,
  leaky boundary.

## Prerequisites

- The Day 70 lesson (read it first — it walks the method this lab applies).
- Day 69: dataclasses, `field(default_factory=...)`, `frozen=True`, and type
  hints.
- Day 68: composition versus inheritance, and the dunder protocols
  (`__eq__`, `__hash__`, `__add__`, `__str__`).
- Day 67: classes, instances, `__init__`, methods and attributes.
- Day 66: raising exceptions on purpose and designing an exception hierarchy.
- Days 64–65: reading and writing text files, and JSON.
- Day 63: the pure core and the thin shell, which this lab promotes from
  functions to types.
- A text editor and a terminal. Nothing beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python` for
  `python3`. The roster header contains an em dash, so a UTF-8 terminal is
  needed for it to render; the numbers are unaffected either way.

## Hardware requirements

Any computer that runs Python 3. The whole lab is under 1,200 lines of text
and code, the club it builds has three members, and the JSON file it writes is
about 1 KB. No special memory, disk, GPU, or network.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0). The lab uses
  `dataclasses(frozen=True)`, `enum.Enum`, `re`, `datetime`, `json` and
  `pathlib` — all standard library.
- `bash` for the test runner (preinstalled on macOS and Linux).
- Nothing to install. See [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed at any
point. The lesson's Alternatives section discusses `sqlite3` (also standard
library), SQLAlchemy and pydantic (both free and open source, installed with
`pip`) — none of them is required to complete this lab, and the point of the
repository boundary is precisely that you could adopt any of them later by
rewriting one class.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-070-modeling-a-domain-with-objects
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-070-modeling-a-domain-with-objects/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── examples/
│   ├── domain-rules.md             ← the eleven rules and the owner's vocabulary
│   ├── gym_core.py                 ← reference pure domain core (no I/O)
│   ├── gym_repository.py           ← reference JSON repository (the only file-aware module)
│   └── demo.py                     ← reference CLI adapter: roster, round trip, refusals
├── starter/
│   ├── domain-worksheet.md         ← YOUR design work: nouns, classification, invariants, boundaries
│   ├── gym_core.py                 ← YOUR working file (exercises 1–6)
│   ├── gym_repository.py           ← YOUR working file (exercise 7)
│   └── demo.py                     ← provided complete; runs once your core is finished
├── tests/
│   └── run_tests.sh                ← behaviour checks; exits 0 only if all pass
├── expected-output/
│   ├── sample-run.txt              ← real captured session with the reference
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

Running either `demo.py` also creates `club.json` in whatever directory you
run it from. It is safe to delete at any time.

## How to run

From this directory:

```bash
# 1. Read the domain. This is the only specification you get.
cat examples/domain-rules.md

# 2. Model on paper first. Open the worksheet and fill in parts 1-4
#    BEFORE writing any code.
cat starter/domain-worksheet.md

# 3. See the finished reference: the roster, the monthly revenue, a JSON
#    round trip, and every rule being refused in turn.
python3 examples/demo.py club.json

# 4. Look at what the repository wrote — plain, readable data.
head -18 club.json

# 5. Call the pure core directly, with no adapter and no file in sight.
PYTHONPATH=examples python3 -c "import gym_core as g; print(g.Money(2900, 'EUR') + g.Money(4900, 'EUR'))"
PYTHONPATH=examples python3 -c "import gym_core as g; print(g.Money(100, 'EUR') + g.Money(100, 'USD'))"

# 6. Your task: complete exercises 1-6 in starter/gym_core.py, then
#    exercise 7 in starter/gym_repository.py.
python3 starter/demo.py club.json

# 7. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `cat examples/domain-rules.md` — prints the eleven rules the owner stated,
  plus the vocabulary list. Everything you model must come from these
  sentences, and nothing you model should come from anywhere else.
- `cat starter/domain-worksheet.md` — the six-part design worksheet: nouns and
  verbs, the entity-versus-value-object classification, the invariant table
  with an enforcement point for each rule, the boundary table, the
  anti-pattern checklist, and a place to paste your evidence.
- `python3 examples/demo.py club.json` — runs the reference program end to
  end. It prints the roster ordered by membership number, the monthly revenue
  summed into a single `Money`, the result of saving and reloading the club
  through the repository, and then six deliberate rule violations with the
  exact domain error each one raises.
- `head -18 club.json` — shows the first member as the repository wrote them:
  a membership number, a name, an ISO date, a nested plan with whole cents and
  a currency code, and a list of check-in dates. Notice there is no Python in
  there — the file format is the repository's business, not the model's.
- The two `PYTHONPATH=examples` one-liners — import the domain core with no
  adapter, no file and no program around it, and add two money amounts. The
  first succeeds and prints `78.00 EUR`; the second raises `CurrencyMismatch`.
  That is the pure core being exercised directly, which is the property the
  boundary exists to give you.
- `python3 starter/demo.py club.json` — the same reference adapter, driven by
  the core *you* wrote. `demo.py` in `starter/` is provided complete on
  purpose: if you ever feel tempted to put a rule in it, that is the signal
  the rule belongs in `gym_core.py`.
- `bash tests/run_tests.sh` — 33 checks while the starter is unfinished, 46
  once you complete every exercise. Exits 0 only if all of them pass.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured session. The heart of it:

```text
$ python3 examples/demo.py club.json
Northside Gym — roster
  GYM-0001  Ada    joined 2026-01-15  plan basic (29.00 EUR)  April check-ins: 4
  GYM-0002  Grace  joined 2026-02-01  plan plus (49.00 EUR)  April check-ins: 15
  GYM-0003  Ada    joined 2026-03-09  plan basic (29.00 EUR)  April check-ins: 0
  monthly revenue: 107.00 EUR

Saved to club.json and reloaded — round trip intact: True

Rules the model refuses to break
  a membership number that is not GYM-####: InvalidMembershipNumber: membership number must look like GYM-0001, got '0007'
  a negative price: InvalidMoney: money cannot be negative, got -100 cents
  adding dollars to euros: CurrencyMismatch: cannot add USD to EUR
  enrolling a number twice: DuplicateMember: GYM-0001 is already a member of Northside Gym
  a member the club never met: UnknownMember: GYM-9999 is not a member of Northside Gym
  a 13th basic check-in in one month: CheckInLimitExceeded: GYM-0003 is on the basic plan and already used all 12 check-ins in 2026-04
exit: 0
```

Nothing in this lab reads the clock, the network, or a random number, so the
same commands produce the same bytes on any machine with Python 3.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the exact
required behaviour of every value object, entity, the repository, and the CLI
adapter on every platform.

## Validation steps

1. `python3 examples/demo.py club.json` exits 0 and reports
   `round trip intact: True`.
2. The roster shows **two members named Ada** with different membership
   numbers, treated as two different people — rule 3, visible in the output.
3. The monthly revenue is `107.00 EUR`. Check it by hand: 29.00 + 49.00 +
   29.00. Because the amounts are whole cents, that sum is exact by
   construction, not by luck.
4. Grace, on the plus plan, records fifteen April check-ins without complaint;
   the third member's thirteenth basic check-in in one month is refused with
   `CheckInLimitExceeded`.
5. `head -18 club.json` shows plain JSON with `price_cents: 2900` — an
   integer, never a float.
6. The second `PYTHONPATH=examples` one-liner ends in
   `gym_core.CurrencyMismatch: cannot add USD to EUR`.
7. Every row of `starter/domain-worksheet.md` is filled in — including part 5,
   the anti-pattern checklist, in sentences rather than single words.
8. `grep -nE 'import json|import os|from pathlib|open\(|print\(|input\(' starter/gym_core.py`
   finds nothing. The suite checks this too, but do it yourself once.
9. `bash tests/run_tests.sh` reports `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished:
`33 checks, 0 failure(s).` Those 33 are the reference model, the reference
repository, the boundary proofs, and a structural check that your starter is
valid Python, defines every required class, and imports nothing that does I/O.

Once you complete all seven exercises the suite stops testing structure and
holds your files to exactly the same strict standard as the reference, giving
`46 checks, 0 failure(s).` The command exits 0 on success and non-zero on any
failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

The suite is worth reading before you run it. Two checks in particular explain
the whole design: `check_purity` reads your core's imports and fails if it can
reach the outside world, and `check_core` runs every model assertion from a
directory created with `mktemp -d` that contains no files at all — so a rule
that needs a file on disk cannot pass.

## Cleanup

The lab writes only `club.json`, into whatever directory you ran a demo from:

```bash
rm -f club.json
```

To reset your work, restore the starter from git:
`git checkout -- starter/`. The test runner makes its own temporary
directories with `mktemp -d` and removes each one as that check finishes, so a
completed run leaves nothing behind.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: the
`NotImplementedError` raised by every unfinished exercise, the
`FrozenInstanceError` that means your value object is working correctly, the
`TypeError: unhashable type` that follows defining `__eq__` without
`__hash__`, `ModuleNotFoundError: No module named 'gym_core'` when a file is
run from the wrong directory, the recursion that comes of calling `self ==`
inside `__eq__`, why `Money(True, "EUR")` must be refused, and what to do when
the purity check fails.

## Security notes

See [security.md](security.md). Short version: validation at construction is a
security control — when the only way to obtain a `Member` is through code that
checks the membership number, the price and the currency, a hand-edited file
cannot inject a negative price or an unknown tier. The core imports nothing
capable of I/O, so it physically cannot delete a file or open a socket
whatever input it is handed. `json.loads` is safe by design; `pickle` is not.
Membership records are personal data, and belong out of version control.

## Extension exercises

1. **Add a third tier.** Introduce a `STUDENT` tier with its own price and its
   own monthly check-in limit. Count the files you had to change. If it was
   more than the enum, the limits table and the plan construction, the closed
   set had leaked somewhere — and you have just found where.
2. **Add a second repository.** Write a `CsvClubRepository` with the same
   `save` and `load` methods, storing one row per member. Then prove the swap
   is free: run the demo against each in turn and confirm the roster, the
   revenue and the round-trip check are identical. If the core needed even one
   edit, the boundary was not where you thought it was.
3. **Model billing.** Add a report that uses the existing `DateRange` to
   produce the amount due for one member over one billing period. Decide
   deliberately — writing your reasoning in the worksheet — whether it belongs
   on `Member`, on `Club`, or in a separate report class. Then state the
   invariant your answer implies, in one sentence, and name the line that
   enforces it.
4. **Break the boundary on purpose.** Add `print("saving...")` to
   `starter/gym_core.py` and run the tests. Watch the purity check fail, then
   remove it. Knowing exactly which check catches a leak is worth more than
   being told the rule.
5. **Refuse the future.** Rule 7 says a check-in never changes, but nothing
   stops a check-in dated a hundred years from now. Decide whether that is a
   rule the owner stated (it is not) and write one sentence in the worksheet
   explaining why you did or did not add it. Restraint is part of modelling.

## Navigation

- **Previous day:** Day 69 — Dataclasses and Type Hints
  (`labs/sections/programming-with-python/day-069-dataclasses-and-type-hints/`).
- **Next day:** Day 71 — the first day of Week 11, Testing and Code Quality
  (`labs/sections/programming-with-python/`, to be written).
- **Week 10 project:** the Expense Tracker
  (`labs/sections/programming-with-python/projects/week-10/`). It applies this
  exact method to the spending domain from the lesson: `Money` as a frozen
  value object, `Category` as an enum, `Expense` and `Ledger` as the model, a
  CSV importer and a repository as adapters, and a report layer on top.
