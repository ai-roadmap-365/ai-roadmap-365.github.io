# Day 069 lab — Records That Write Themselves

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Dataclasses and Type Hints
- **Day number:** 69 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-069-dataclasses-and-type-hints
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-069-dataclasses-and-type-hints` when the site is running.
<!-- generated-links:end -->

## Purpose

On Day 67 you wrote a record class by hand, and on Day 68 you gave it dunder
methods. If you did that honestly you noticed the tedium: for a class holding
three pieces of data you wrote `__init__`, `__repr__` and `__eq__`, and typed
the same field names into each one.

This lab measures that tedium and then deletes it. You start with
`HandWrittenRecord` — 22 lines, 18 of them code, with the name `prompt`
appearing in five distinct places — and rebuild it as a five-line dataclass
that behaves identically. Then you meet the parts `@dataclass` does not
generate: a per-instance list default, validation, a derived field, and a
frozen variant that is safe to use as a dictionary key.

The second half is about the annotations themselves. `examples/scoring.py`
contains two deliberate contradictions between what its annotations promise
and what its code does, and `examples/inspect_runtime.py` proves the point
that makes them possible: Python **stores** every annotation and **checks**
none of them. You assign a string to a field annotated `float` and watch
nothing happen.

Finally you rebuild `@dataclass` yourself. About forty lines, reading
`__annotations__` and generating three methods, checked field-for-field
against the real decorator. After that it stops being magic.

## Learning objectives

- Convert a hand-written record class into a dataclass and confirm the
  generated `__repr__` and `__eq__` behave the same as the ones you wrote.
- Trigger the mutable default trap in both its forms — silently shared in a
  plain function signature, refused with a `ValueError` in a dataclass — and
  fix it with `field(default_factory=list)`.
- Add `__post_init__` validation and a derived field that is not a
  constructor parameter.
- Build a frozen, ordered dataclass and use it as a dictionary key, then
  watch `FrozenInstanceError` refuse an assignment.
- Round-trip records through JSON with `asdict`, rebuild them, and prove the
  trip was lossless using the generated `__eq__`.
- Demonstrate at runtime that annotations are stored in `__annotations__` and
  read by `dataclasses.fields()`, yet never enforced against any value.
- Implement a `mini_dataclass` decorator from scratch and verify it against
  the real `@dataclass`.

## Prerequisites

- The Day 69 lesson (read it first — it walks these exact cases).
- Day 68: dunder methods, especially `__eq__` and `__hash__`, and why
  defining `__eq__` costs you the inherited hash.
- Day 67: classes, `__init__`, and attributes.
- Day 66: raising `ValueError` and `TypeError` deliberately.
- Day 65: `json.dumps` and `json.loads`.
- Days 57-63: functions, decorators, and modules.
- A text editor and a terminal. Nothing beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3`. Nothing in this lab touches paths, encodings, or line
  endings, so behaviour is identical everywhere.

## Hardware requirements

Any computer that runs Python 3. Every file here is a few kilobytes of source
and the lab creates no data files at all. No special memory, disk, or GPU.

## Required software

- `python3` (**3.10 or newer** — the lab uses `list[str]` field annotations
  and modern dataclass behaviour; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — `dataclasses`, `json`, `sys`, and `pathlib`.
  Nothing to install. See [`requirements/README.md`](requirements/README.md).
- **Optional and not required:** a static type checker (mypy or pyright) for
  one optional step. None is installed in this lab's environment, and
  `examples/check_types.sh` handles its absence cleanly.

## Free and open-source options

Everything here is free and open source: Python, bash, and the standard
library. No account, API key, network access, or purchase is needed.
`dataclasses` and `typing` ship with Python itself. The optional type
checkers, mypy and pyright, are both free and open source too — pyright is
also the engine behind the Pylance extension for VS Code — but this lab
deliberately requires neither.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-069-dataclasses-and-type-hints
python3 --version   # confirm Python 3.10+ is available
```

## File structure

```text
day-069-dataclasses-and-type-hints/
├── README.md                    ← you are here
├── metadata.yml                 ← machine-readable lab metadata
├── starter/
│   ├── records.py               ← YOUR working file (exercises 1–6)
│   ├── mini_dataclass.py        ← YOUR working file (exercise 7)
│   └── demo.py                  ← given driver; runs YOUR code, exercise by exercise
├── examples/
│   ├── records.py               ← complete reference: hand-written vs dataclass, validation, JSON
│   ├── mini_dataclass.py        ← complete reference: @dataclass rebuilt in ~40 lines
│   ├── demo.py                  ← guided tour of the reference (exercises 1–5 and 7)
│   ├── inspect_runtime.py       ← exercise 6: what Python stores, and what it ignores
│   ├── scoring.py               ← an annotated file with two deliberate type errors
│   └── check_types.sh           ← OPTIONAL: runs a type checker if one exists, skips cleanly if not
├── tests/
│   └── run_tests.sh             ← behaviour checks; exits 0 only if all pass
├── expected-output/
│   ├── sample-run.txt           ← real captured session with the reference
│   └── test-run.txt             ← real captured run of the test suite
├── requirements/
│   └── README.md                ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

This lab writes **no files at all**. There is nothing to clean up but Python's
own bytecode cache.

## How to run

From this directory:

```bash
# 1. Read the two record classes side by side — count the lines.
cat examples/records.py

# 2. See the finished reference: exercises 1-5 and 7 in one guided tour.
python3 examples/demo.py

# 3. Exercise 6 — the proof that annotations are stored but never enforced.
python3 examples/inspect_runtime.py

# 4. OPTIONAL. Runs a type checker over examples/scoring.py if one is
#    installed, and explains what it would find if not. Exits 0 either way.
bash examples/check_types.sh

# 5. See which of scoring.py's two planted bugs Python itself notices.
python3 examples/scoring.py

# 6. Your task: complete exercises 1-6 in starter/records.py and
#    exercise 7 in starter/mini_dataclass.py, then run your version.
python3 starter/demo.py

# 7. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `cat examples/records.py` — shows `HandWrittenRecord` (22 lines, 18 of code)
  immediately above `EvalRecord`, the dataclass that replaces it. The comment
  above the hand-written class asks you to count how many times the name
  `prompt` appears; the answer is five distinct places, seven occurrences.
- `python3 examples/demo.py` — runs six labelled sections: the hand-written
  class beside the dataclass; the mutable default trap in both forms;
  `__post_init__` validation and the derived `prompt_length`; a frozen
  `RunKey` used as a dictionary key and sorted; a JSON round trip via
  `asdict` with `replace()` making a validated copy; and the from-scratch
  `mini_dataclass` compared against the real one. Every line is deterministic
  — no clocks, no random numbers, no memory addresses — so it matches
  `expected-output/sample-run.txt` character for character.
- `python3 examples/inspect_runtime.py` — prints `EvalRecord.__annotations__`
  and the `Field` objects from `dataclasses.fields()`, then assigns a string
  to a field annotated `float` and an integer to one annotated `list[str]`,
  and calls a function annotated `(number: int) -> int` with the string
  `'ab'`. Nothing raises. That is the whole lesson in one script.
- `bash examples/check_types.sh` — looks for `mypy` or `pyright` on your
  `PATH`, then for an importable `mypy` module. If it finds one it runs it
  over `examples/scoring.py` and reports the result. **If it finds none it
  says so and describes the two planted errors without inventing a message.**
  It exits 0 in both cases, because this lab requires no checker.
- `python3 examples/scoring.py` — runs the file with the two planted bugs.
  Only one of them crashes. That asymmetry is the argument for a checker:
  one bug costs you a traceback, the other costs you a wrong value that
  travels silently.
- `python3 starter/demo.py` — the same tour, driven by the functions you
  write. Each exercise runs on its own, so an unfinished one prints a note
  instead of stopping the script.
- `bash tests/run_tests.sh` — real behaviour assertions, not file-existence
  checks: generated `__repr__` and `__eq__`, the mutable-default `ValueError`,
  `__post_init__` validation, frozen hashing and `FrozenInstanceError`, a JSON
  round trip, runtime introspection, and the from-scratch decorator. Exits 0
  only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured session. The heart of it:

```text
$ python3 examples/demo.py

1. Hand-written class vs dataclass
----------------------------------
hand-written repr: HandWrittenRecord(prompt='2+2?', expected='4', score=0.0)
dataclass repr:    EvalRecord(prompt='2+2?', expected='4', score=0.0, tags=[])
hand-written equal by value: True
dataclass equal by value:    True
dataclass differs when a field differs: False

2. The mutable default trap
---------------------------
plain function, call 1: ['math']
plain function, call 2: ['math', 'logic'] <- the list was shared
dataclass refuses it: ValueError: mutable default <class 'list'> for field tags is not allowed: use default_factory
default_factory gives each instance its own list:
  first.tags = ['math']
  second.tags = []
```

Note the contrast in section 2: the plain function shares one list and says
nothing, while the dataclass refuses at class-creation time and names the fix.

The frozen record, and the proof it is hashable:

```text
4. A frozen dataclass is hashable and orderable
-----------------------------------------------
key: RunKey(suite='arithmetic', seed=7)
equal keys hash the same: True
usable as a dict key: 12
sorted by suite then seed: [RunKey(suite='arith', seed=1), RunKey(suite='arith', seed=9), RunKey(suite='geo', seed=2)]
assignment refused: FrozenInstanceError: cannot assign to field 'seed'
```

And the runtime proof that annotations are recorded but never applied:

```text
$ python3 examples/inspect_runtime.py
dataclasses.fields(EvalRecord):
  prompt: str = (required)
  expected: str = (required)
  score: float = 0.0
  tags: list[str] = factory list()
  prompt_length: int = 0

What Python does NOT check
--------------------------
assigned a str to .score -> 'not a number'
assigned an int to .tags  -> 17

double.__annotations__ names: ['number', 'return']
double('ab') -> 'abab'
```

The optional checker step, captured on the authoring machine where **no
checker is installed** — a normal result for a lab that installs nothing:

```text
$ bash examples/check_types.sh
No static type checker is installed, so this optional step is skipped.

This lab needs no installs and no network, so that is a normal result.
A checker reads examples/scoring.py WITHOUT running it and reports
the two planted contradictions between the annotations and the code:
  * label() promises to return str but returns record.score, a float
  * main() passes one EvalRecord where mean_score wants list[EvalRecord]
```

Everything is deterministic, so your output will match — except that
`check_types.sh` will print the checker's own report instead if you happen to
have mypy or pyright installed.

## Validation steps

1. `python3 examples/demo.py` exits 0 and section 1 shows the hand-written
   and dataclass reprs differing only in the class name and the extra `tags`
   field.
2. Section 2 shows the plain function returning `['math', 'logic']` on its
   second call — the shared list — and the dataclass raising `ValueError`
   with a message containing `use default_factory`.
3. Section 3 reports `derived prompt_length: 18` and rejects both the blank
   prompt and the score of 3.0, with the offending `3.0` in the message.
4. Section 4 reports `equal keys hash the same: True`, `usable as a dict
   key: 12`, and refuses the assignment with `FrozenInstanceError`.
5. Section 5 reports `rebuilt == original: True` — a value-equality assertion
   that only works because `@dataclass` generated `__eq__`.
6. Section 7 reports `same repr shape (fields and formatting): True`, meaning
   your from-scratch decorator formats identically to the real one.
7. `python3 examples/inspect_runtime.py` exits 0 having assigned a string to
   a `float` field and an integer to a `list[str]` field with **no error**.
8. `bash examples/check_types.sh` exits 0 and states clearly whether a
   checker was found.
9. Complete exercises 1-7 in `starter/`, run `python3 starter/demo.py`, and
   confirm it matches the reference.
10. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished:
`33 checks, 0 failure(s).` The suite always holds the reference in
`examples/` to a strict standard; while your `starter/` files still contain
`NotImplementedError` it checks their structure only. Once you finish all
seven exercises, the suite runs the same strict behaviour checks against your
files too, so the check count rises. The command exits 0 on success and
non-zero on any failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

This lab creates no data files and no output directory — there is nothing to
delete. Python may leave a bytecode cache behind; the test runner sets
`PYTHONDONTWRITEBYTECODE=1` so it does not, but if you ran the scripts
directly you can remove it:

```bash
rm -rf examples/__pycache__ starter/__pycache__
```

To reset your work, restore the starter from git: `git checkout -- starter/`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: the
`ValueError` on a mutable default (which is the exercise working), `TypeError:
non-default argument follows default argument`, a `__post_init__` that never
runs, `TypeError: unhashable type` on a record used as a dict key,
`FrozenInstanceError` when you meant to update a field, the very common
"my annotation does not work" (it is not supposed to), what to do when
`check_types.sh` reports no checker installed, and the `NotImplementedError`
the starter raises by design.

## Security notes

See [security.md](security.md). Short version: **a type hint is not a
validation and must never be treated as one at a trust boundary** — a checker
reasons about your source, never about the value that actually arrived, so
`__post_init__` is the only gate that runs. The generated `__repr__` prints
every field, so a secret in a dataclass is a secret in your logs unless you
mark that field `repr=False`. `frozen=True` prevents accidental mutation, not
a determined attacker. And never rebuild objects from untrusted data with
anything that executes it.

## Extension exercises

1. **Make the mini decorator refuse mutable defaults.** The real `@dataclass`
   raises `ValueError` for a `list`, `dict` or `set` default. Add that check
   to `mini_dataclass`, then add your own `default_factory` support, and
   confirm your version behaves like the real one on both cases.
2. **Add `frozen=True` to the mini decorator.** Install a `__setattr__` that
   raises after construction (the tricky part is letting `__init__` itself
   assign), and generate a `__hash__` from the field values.
3. **Write a runtime checker.** Build a `@checked` decorator that walks
   `dataclasses.fields(self)` after `__init__` and raises `TypeError` for any
   value failing `isinstance` against its annotation. Handle `str`, `int`,
   `float` and `bool`, then decide deliberately what to do about `list[str]`,
   where `isinstance(value, list)` works but the element type does not.
   Writing that limitation down is the shortest explanation of why pydantic
   is a substantial library rather than a decorator.
4. **Compare the four record types.** Implement the same three-field record as
   a hand-written class, a dataclass, a `typing.NamedTuple`, and a
   `collections.namedtuple`. For each, record the lines of code, whether
   instances are mutable, hashable, and unpackable, whether they compare equal
   to a plain tuple, and what `repr` prints. Then say which you would pick for
   a dictionary key and which for a mutable working record.

## Navigation

- **Previous day:** Day 68 — Inheritance, Composition, and Dunder Methods
  (`labs/sections/programming-with-python/day-068-inheritance-composition-and-dunder-methods/`).
- **Next day:** Day 70 — Modeling a Domain with Objects
  (`labs/sections/programming-with-python/day-070-modeling-a-domain-with-objects/`,
  to be written).
- **Week 10 project:** the Expense Tracker. The typed, validated record you
  build here is exactly the shape its expense entries want to be.
