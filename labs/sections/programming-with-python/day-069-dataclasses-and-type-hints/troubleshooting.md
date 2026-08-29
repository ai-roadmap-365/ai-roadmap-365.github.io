# Troubleshooting — Day 069 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and
most Linux systems, bare `python` may be missing or point to an old version.
Check with `python3 --version`; this lab needs 3.10 or newer.

## `TypeError: 'type' object is not subscriptable`

Your Python is older than 3.9, so it cannot read `list[str]` as an
annotation. Check `python3 --version`. If you are stuck on an older Python,
`from typing import List` and `List[str]` means the same thing — but the
lab and the lesson both use the modern spelling, so upgrading is the better
answer.

## The starter raises `NotImplementedError` when I run it

That is expected until you finish the seven exercises in
`starter/records.py` and `starter/mini_dataclass.py`. Each unfinished piece
raises `NotImplementedError` on purpose so an empty function can never be
mistaken for a working one. `starter/demo.py` runs each exercise separately
and prints a note for the unfinished ones rather than stopping, so you can
work through them in order and watch the notes disappear.

## `ValueError: mutable default <class 'list'> for field tags is not allowed: use default_factory`

**This is exercise 2 working, not a bug.** You wrote `tags: list[str] = []`
and the dataclass refused it at class-creation time, before any instance
existed. The reason is that one list would be shared by every instance. The
message names the fix:

```python
tags: list[str] = field(default_factory=list)
```

Notice what the equivalent mistake does in a plain function signature —
`def add_tag(tag, bucket=[])` — and see section 2 of `examples/demo.py`:
Python permits it, shares one list across every call, and never warns you.
The dataclass version is the loud, helpful form of the same trap.

## `TypeError: non-default argument 'x' follows default argument`

The generated `__init__` is an ordinary function signature, so fields with
defaults must come after fields without them. Either reorder the
declarations so the required ones come first, or pass `kw_only=True` to
`@dataclass`, which makes every field keyword-only and removes the ordering
constraint entirely.

## `__post_init__` never runs

Three usual causes. Check the spelling — two underscores on each side.
Check you did not also write your own `__init__`, which replaces the
generated one and with it the call to `__post_init__`. And check the class
actually has the `@dataclass` decorator; without it the class body is just
annotations and nothing is generated at all.

## `TypeError: unhashable type: 'RunKey'`

The class generated `__eq__` but is not frozen, so it has no `__hash__`.
This is Day 68's rule: defining `__eq__` removes the inherited hash, because
two objects that compare equal must hash equal and an identity hash cannot
promise that. Add `frozen=True`:

```python
@dataclass(frozen=True, order=True)
class RunKey:
    suite: str
    seed: int
```

Now assignment is blocked, so the field values can never change, so a
generated hash can never go stale — and `@dataclass` supplies one.

## `FrozenInstanceError: cannot assign to field 'seed'`

If you were testing exercise 4, this is the guarantee working. If you
genuinely need a changed record, build a copy rather than mutating:

```python
from dataclasses import replace
updated = replace(key, seed=8)
```

`replace` calls `__init__` with the merged fields, so `__post_init__` runs
and the new value is validated.

## My annotation "does not work" — a string went into a `float` field

It is not supposed to do anything. This is the central point of the day, not
a misconfiguration. Python evaluates each annotation once, stores it in
`__annotations__` for tools to read, and never compares any value against
it. Prove it to yourself:

```bash
python3 examples/inspect_runtime.py
```

You will see a string assigned to a field annotated `float`, an integer
assigned to one annotated `list[str]`, and a function annotated
`(number: int) -> int` returning `'abab'` when called with `'ab'` — all with
nothing raised. If you need enforcement at runtime, write it in
`__post_init__`, or use a library such as pydantic that does it for you.

## `bash examples/check_types.sh` says no static type checker is installed

**That is a normal, expected result.** This lab installs nothing and uses no
network, and no checker is installed in this environment. The script detects
that, describes the two errors a checker would find in `examples/scoring.py`,
and exits 0. Nothing in the lab or its tests requires a checker.

If you want one on your own machine, both mypy and pyright are free and open
source. Install into a virtual environment (Day 43), not your system Python:

```bash
python3 -m pip install mypy
python3 -m mypy examples/scoring.py
```

Two notes if you do. First, a checker exits **non-zero** when it finds
errors — for `scoring.py` that is the success case, since the errors are
planted deliberately, and `check_types.sh` reports the status rather than
propagating it. Second, this README quotes no verbatim checker message
anywhere, because none was produced on the authoring machine; what a checker
prints, and in what wording, is for you to read from your own run.

## `python3 examples/scoring.py` crashes — is that the type error?

Partly, and the partial answer is the interesting one. `scoring.py` contains
two planted contradictions. `main()` passes a single `EvalRecord` where
`mean_score` is annotated to take `list[EvalRecord]`, and that one does
crash, because the function tries to iterate a single record. The other —
`label()` declared `-> str` while returning `record.score`, a float — does
**not** crash at all; the function simply returns the wrong type and any
caller carries on with it. One bug costs you a traceback, the other costs
you a wrong value that travels silently. That asymmetry is the argument for
running a checker.

## `ModuleNotFoundError: No module named 'records'`

The drivers import the module sitting beside them. Run them by path from the
lab directory (`python3 examples/demo.py`, `python3 starter/demo.py`) rather
than copying one file elsewhere, and the import resolves — each driver puts
its own directory on `sys.path` for exactly this reason.

## `starter/demo.py` uses my old code after I edited a file

A stale bytecode cache, or an editor that has not saved. Save, then remove
the cache and re-run:

```bash
rm -rf starter/__pycache__ examples/__pycache__
python3 starter/demo.py
```

## The test suite fails but the demo looks fine

Read the first failing `FAIL:` line — each check names the behaviour it
tested. The most common causes are a `describe_fields` whose strings do not
match the required format exactly (the suite compares
`'tags: list[str] = factory list()'` character for character), an
`annotation_names` that sorts or filters instead of returning declaration
order, or a `mini_dataclass.__eq__` that returns `False` rather than
`NotImplemented` when handed an object of a different class.

## The test count is not the number I expected

The suite reports `33 checks, 0 failure(s).` while your starter still
contains `NotImplementedError`, because it checks the starter's structure
only at that stage. Once every exercise is complete it runs the full strict
behaviour suite against your files as well as the reference, so the count
rises. Both are correct results; what must always be true is
`0 failure(s).` and an exit status of 0.
