# Troubleshooting — Day 070 lab

## `python: command not found`

Use `python3` explicitly, as every command in this lab does. On macOS and most
Linux systems, bare `python` may be missing or point to an old version. Check
with `python3 --version`.

## The starter raises `NotImplementedError`

Expected until you finish the exercises. Every unfinished method raises
`NotImplementedError` on purpose so that an empty function can never be
mistaken for a working one:

```text
NotImplementedError: Exercise 2a: validate the money amount
```

Exercises 1–6 are in `starter/gym_core.py`; exercise 7 (in three parts) is in
`starter/gym_repository.py`. `starter/demo.py` is provided complete and needs
no editing — it will start working the moment the core and the repository do.

## `dataclasses.FrozenInstanceError: cannot assign to field 'value'`

Your value object is working exactly as designed. A frozen dataclass refuses
assignment after construction, which is what stops a `MembershipNumber` or a
`Money` from drifting away from the value that was validated:

```text
FrozenInstanceError | cannot assign to field 'value'
```

The fix is never to unfreeze it. Build a **new** value instead — that is what
value objects are for. Where you were about to write an assignment to a price,
write `member.switch_plan(Plan(tier, Money(new_cents, "EUR")))` instead.

If you hit this on an *entity*, you have misclassified it: a `Member` has to
change over time, so `Member` is a plain `@dataclass`, not a frozen one.

## `TypeError: ... unhashable type: 'Member'`

You defined `__eq__` on the entity and did not define `__hash__`. Python sets
`__hash__` to `None` for any class that defines `__eq__` without it, on the
reasoning that two objects which compare equal must hash equal, and it will
not guess how. The object then cannot go into a set or be used as a dict key:

```text
TypeError | cannot use 'E' as a set element (unhashable type: 'E')
```

(The exact wording varies between Python versions; the phrase `unhashable
type` is the constant.) The fix is exercise 4b — hash the identity, not the
whole object:

```python
def __hash__(self):
    return hash(self.number)
```

That is also *correct*, not merely a workaround: the identity is the one thing
about a member that never changes, so it is the only safe thing to hash.

## `RecursionError` inside `__eq__`

You wrote something like `return self == other.number` or compared the whole
object to itself inside its own equality method, so `__eq__` calls `__eq__`
forever. Compare the **identity fields**, not the objects:

```python
def __eq__(self, other):
    if not isinstance(other, Member):
        return NotImplemented
    return self.number == other.number
```

The `isinstance` guard matters too. Returning `NotImplemented` (not `False`)
for an unrelated type lets Python try the other object's comparison before
giving up, which is the documented protocol.

## `Money(True, "EUR")` is accepted and it should not be

In Python, `bool` is a subclass of `int`, so `isinstance(True, int)` is `True`
and a plain integer check lets `True` through as the number 1. Exercise 2a
asks you to reject it explicitly:

```python
if not isinstance(self.cents, int) or isinstance(self.cents, bool):
    raise InvalidMoney(...)
```

The reference refuses it with `money must be a whole number of cents, got
True`. A float is refused the same way — `Money(29.0, "EUR")` gives `money
must be a whole number of cents, got 29.0` — because whole cents are the whole
point.

## `ValueError: 'pluss' is not a valid PlanTier`

Working as intended, and worth pausing on. This is the enum catching a typo at
the moment it is written. Had the tier been a plain string, `"pluss"` would
have been accepted, stored, written to the JSON file, and surfaced weeks later
as a member whose check-in limit nobody could explain. Fix the spelling, and
notice that the legal values live in exactly one place.

## `ModuleNotFoundError: No module named 'gym_core'`

The core is not on the import path. Two situations:

- Running a one-liner: set the path explicitly, as the README does —
  `PYTHONPATH=examples python3 -c "import gym_core as g; ..."` (or
  `PYTHONPATH=starter` to exercise your own).
- Running a lab file: run it by path from the lab directory
  (`python3 examples/demo.py club.json`). Python puts the script's own
  directory on the path, so `demo.py` finds its siblings — but only if you
  gave it the path to the right copy. Mixing them (`starter/demo.py` expecting
  your core) is fine; mixing them across directories is not.

## The purity check fails: `starter/gym_core.py imports nothing that does I/O`

The test suite read your core and found something that can touch the outside
world. Search for the usual suspects and move each one out to
`gym_repository.py` or `demo.py`:

```bash
grep -nE 'import json|import os|import sys|from pathlib|open\(|print\(|input\(' starter/gym_core.py
```

A `print` added for debugging is the most common cause. Delete it and raise a
domain error instead — that is what the error hierarchy is for, and unlike a
`print` it can be tested.

## A model check fails with a missing-file error

The suite runs your core from a directory created with `mktemp -d` that
contains nothing at all. If a rule fails there but works in the lab directory,
the rule is quietly depending on a file — which means the boundary has leaked
in a way the import scan did not catch. Trace what the failing method reads.

## `bash: tests/run_tests.sh: Permission denied`

Run it through bash explicitly, as the README shows: `bash tests/run_tests.sh`.
You do not need to `chmod +x` anything.

## The check count is 33 and I expected 46

33 is correct while any exercise is unfinished: the suite detects
`NotImplementedError` in your starter files and switches to structural checks
only, printing `Note: starter/ still has unfinished exercises`. Finish all
seven exercises — including the three parts of exercise 7 — and the suite runs
the full model, repository and demo checks against your files, giving
`46 checks, 0 failure(s).`

## I want to start over

Delete the generated file and restore the starter from git:

```bash
rm -f club.json
git checkout -- starter/
```
