# Day 068 lab — Protocols and Hierarchies

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Inheritance, Composition, and Dunder Methods
- **Day number:** 68 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-068-inheritance-composition-and-dunder-methods
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-068-inheritance-composition-and-dunder-methods` when the site is running.
<!-- generated-links:end -->

## Purpose

Make inheritance fail on purpose, then make it work; predict a method
resolution order before the interpreter tells you the answer; rebuild the
same design with composition and write down which one you would keep; and
then implement enough of Python's data model that `len()`, indexing,
slicing, `for`, `in`, `==`, `sorted()`, `max()`, `set()` and `with` all work
on a class you wrote this afternoon — with none of those builtins modified
in any way.

That last point is the whole lab. Interoperability in Python is not a
courtesy that library authors extend to you; it is a set of method names. A
`DataLoader` written years before your data existed can iterate your dataset
class because your class implements `__len__` and `__getitem__`. You are
practising that exact protocol here, on a kitchen small enough to hold in
your head.

## Learning objectives

By the end of this lab you can:

- Explain what a subclass `__init__` replaces, and predict where the failure
  surfaces when `super().__init__(...)` is missing — in a later method, not
  in the constructor.
- Derive a diamond hierarchy's MRO by hand from the two C3 rules, then
  confirm it against `__mro__`, and show that `super()` can reach a class the
  current one does not inherit from.
- Model one domain both ways and state a concrete change that breaks the
  inheritance version while leaving the composed version untouched.
- Swap a collaborator object at runtime and observe the behaviour change with
  no class edited and no subclass written.
- Implement `__len__`, `__getitem__`, `__iter__`, `__contains__`, `__eq__`
  with a matching `__hash__`, and `__lt__` under `@total_ordering`, and prove
  each one by driving it with an unmodified builtin.
- Write a context manager whose `__exit__` cleans up even when the body
  raises, and explain what returning `True` from it would do instead.
- Define an `abc.ABC` and show that an incomplete subclass is refused at
  construction, naming the missing method.

## Prerequisites

- Day 68's lesson, "Inheritance, Composition, and Dunder Methods" (read it
  first — this lab is its exercise).
- Day 67: classes, `__init__`, `self`, methods, properties, and
  `__repr__`/`__str__`.
- Day 66: exceptions, `try`/`except`, and raising your own.
- Day 64: file I/O and the `with` statement — whose protocol you implement
  here yourself.
- Comfort running `python3` from a terminal and editing a text file.

## Supported operating systems

macOS and Linux run every command as written. On Windows, use WSL — the
Python is portable, but the test runner is a bash script.

## Hardware requirements

Any machine that runs Python 3. This lab writes no files and generates no
data; it holds a handful of small objects in memory. Disk and memory
requirements are negligible.

## Required software

- `python3` 3.8 or newer (tested on 3.14.0)
- `bash` for the test runner

Nothing else. No pip install, no network access, no privileges, no API keys.
See `requirements/README.md` for details.

## Free and open-source options

Everything here is free and open source. Python is released under the PSF
License, and every module used — `abc`, `functools`, `collections.abc`,
`typing` — is part of the standard library. There is nothing to buy, no
paid tier, and no account to create. The one third-party alternative
mentioned in the lesson, `attrs`, is also free and open source, and this lab
deliberately does not need it.

## Installation

```bash
cd labs/sections/programming-with-python/day-068-inheritance-composition-and-dunder-methods
python3 --version
```

If that prints `Python 3.8` or higher, you are ready. There is nothing to
install.

## File structure

```
day-068-inheritance-composition-and-dunder-methods/
  README.md                      this file
  metadata.yml                   lab metadata and the recorded execution evidence
  examples/
    01_inheritance_super.py      step 1: the missing super() call, broken then fixed
    02_mro_diamond.py            step 2: the four-class diamond and its MRO
    03_composition.py            step 3: one domain modelled both ways
    kitchen.py                   step 4: the reference container class (Dish, Menu)
    05_context_manager.py        step 5: __enter__/__exit__ and the cleanup guarantee
    06_abstract_base.py          step 6: abc.ABC, and the duck typing that replaces it
  starter/
    kitchen.py                   your copy, with six numbered exercises to complete
    comparison.md                worksheet for the written answers in steps 2 and 3
  tests/
    run_tests.sh                 assert-based suite; 36 checks against real behaviour
  expected-output/
    sample-run.txt               captured output of every example script
    test-run.txt                 captured output of the test suite
  requirements/README.md         dependencies and platform notes
  troubleshooting.md             symptom-by-symptom fixes
  security.md                    implicit dunder execution, trust, and what to keep out
```

Step 4 has no numbered script because the container class *is* the file you
edit: `starter/kitchen.py`, with `examples/kitchen.py` as the reference to
compare against once you have tried.

## How to run

Work through the six steps in order. Each one is short and each one has a
point you should be able to state before moving on.

```bash
python3 examples/01_inheritance_super.py
```

Then — and this matters — write your MRO prediction into
`starter/comparison.md` **before** running the next one:

```bash
python3 examples/02_mro_diamond.py
python3 examples/03_composition.py
```

Now the main build. Open `starter/kitchen.py` and complete its six numbered
exercises, running the file after each one:

```bash
python3 starter/kitchen.py
```

It stops at exercise 1 until you implement `__len__`, then gets further with
each method you finish. Compare against the reference only after you have
tried:

```bash
python3 examples/kitchen.py
```

Finish with the context manager and the abstract base class, then run the
suite:

```bash
python3 examples/05_context_manager.py
python3 examples/06_abstract_base.py
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/01_inheritance_super.py` — constructs a subclass whose
  `__init__` never calls `super().__init__()`, shows that construction
  *succeeds*, then calls `describe()` and catches the `AttributeError` that
  surfaces there. Then runs the fixed class for contrast.
- `python3 examples/02_mro_diamond.py` — builds `ToasterOven(Heater, Timer)`
  where both bases inherit from `Appliance`, prints `__mro__`, runs the
  cooperative `super()` chain through all four classes, and finally asks the
  interpreter to build a hierarchy C3 cannot linearise so you see the refusal.
- `python3 examples/03_composition.py` — runs the same domain as a hierarchy
  and as an object graph, asserts nothing but prints both, and then swaps a
  `HeatingElement` for a `FanAssistedElement` at runtime.
- `python3 starter/kitchen.py` — your container class, driven by fourteen
  lines of plain builtins. Each unfinished exercise raises
  `NotImplementedError` naming what to write.
- `python3 examples/kitchen.py` — the same driver against the finished
  reference, so you can diff your output against the target.
- `python3 examples/05_context_manager.py` — runs a `with` block twice, once
  succeeding and once raising, to show `__exit__` runs both times.
- `python3 examples/06_abstract_base.py` — instantiates a complete subclass,
  then an incomplete one, then shows a class that satisfies `Iterable`
  without inheriting from anything.
- `bash tests/run_tests.sh` — 36 assertions run in a throwaway directory
  created with `mktemp -d` and removed by an `EXIT` trap.

## Expected output

`python3 examples/kitchen.py` produces exactly this (captured on the
authoring machine; the lab is deterministic, so it reproduces byte for byte):

```text
len: 3
index: Dish('Ramen', 12) | slice: [Dish('Gyoza', 8), Dish('Salad', 4)]
iterate: ['Ramen', 'Gyoza', 'Salad']
contains: True | False
equal: True | False
eq other type: False
hash equal: True
lt: False | ge (total_ordering): True
sorted: [Menu('Lunch', 3 dishes), Menu('Dinner', 2 dishes)]
max: Menu('Lunch', 3 dishes)
longest dish: Dish('Ramen', 12)
sum minutes via comprehension: 24
set of menus: 2
list(): 2
```

Every one of those lines is a builtin operating on a class that inherits
from nothing. `sorted` used only `__lt__`; `max(..., key=len)` used
`__len__`; `set of menus: 2` rather than `3` is `__eq__` and `__hash__`
collapsing the two equal menus.

The other steps produce:

```text
$ python3 examples/01_inheritance_super.py
-- broken: subclass __init__ never calls super().__init__() --
constructed fine: BrokenOven, capacity_litres = 60
AttributeError: 'BrokenOven' object has no attribute 'name'

$ python3 examples/02_mro_diamond.py
ToasterOven -> Heater -> Timer -> Appliance -> object
ToasterOven: ready -> Heater: elements warming -> Timer: clock started -> Appliance: power on
Heater's super() lands on: Timer
Heater actually inherits from: ['Appliance']

$ python3 examples/05_context_manager.py
[service open] Bad night
[service closed] Bad night
caught: burnt the souffle | open = False

$ python3 examples/06_abstract_base.py
TypeError: Can't instantiate abstract class PastryStation without an implementation for abstract method 'prepare'
```

The full capture of every script is in `expected-output/sample-run.txt`; the
suite's output is in `expected-output/test-run.txt`.

## Validation steps

You are done when every box is checked:

- [ ] `python3 examples/01_inheritance_super.py` shows the object being
      constructed successfully and *then* failing in `describe()`, and exits 0.
- [ ] You wrote your predicted MRO into `starter/comparison.md` **before**
      running step 2, and it matched
      `ToasterOven -> Heater -> Timer -> Appliance -> object`.
- [ ] You can say why `Appliance` appears in that list once and not twice.
- [ ] `python3 examples/03_composition.py` shows the runtime swap changing
      `heating to` into `fan-assisted to` with no class edited.
- [ ] `starter/comparison.md` has a real answer on every `Your answer:` line,
      including a concrete base-class edit that breaks only the inherited
      version.
- [ ] `python3 starter/kitchen.py` runs with no `NotImplementedError` and its
      output matches `python3 examples/kitchen.py` line for line.
- [ ] `python3 examples/05_context_manager.py` shows `[service closed]`
      printing in the run whose body raises, *before* the `caught:` line.
- [ ] `python3 examples/06_abstract_base.py` raises `TypeError` naming
      `prepare`.
- [ ] `bash tests/run_tests.sh` prints `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

The suite checks real behaviour, not file existence: that the broken
subclass *constructs* and only then fails, and that the traceback names
`describe` and not `__init__`; that the diamond's MRO is exactly the C3
answer with the shared base listed once; that `Heater` genuinely does not
inherit from `Timer` even though its `super()` lands there; that an
inconsistent hierarchy is refused at class-definition time; that both
designs of the appliance domain produce identical behaviour while the
composed classes inherit nothing but `object`; that swapping a collaborator
changes the result; that `sorted()` really orders by `__lt__` and that
`@total_ordering` derived `>`, `>=` and `<=`; that `__eq__` returns
`NotImplemented` rather than `False` for unknown types; that a set of three
menus collapses to two and an equal menu finds the same dict entry; that
`__exit__` runs after both a clean and a raising exit without swallowing the
exception; and that the ABC names its outstanding method.

While `starter/kitchen.py` still contains `NotImplementedError`, the suite
checks its structure only and says so. Once you have completed it, the same
full protocol checks run against your version too, and the suite grows from
36 checks to 39.

It exits 0 on success and non-zero on any failure.

Recorded evidence: on the authoring machine (macOS, Apple Silicon, Python
3.14.0) the suite reports `36 checks, 0 failure(s).` and exits 0.

## Cleanup

```bash
git checkout -- starter/kitchen.py starter/comparison.md   # optional: reset your work
```

Nothing else is needed. This lab creates no files, writes nothing outside
its own directory, and opens no network connections. The test suite cleans
up after itself automatically — its scratch directory is created with
`mktemp -d` and removed by an `EXIT` trap.

## Troubleshooting

See `troubleshooting.md` for symptom-by-symptom fixes, including
`AttributeError` in a method rather than the constructor, `TypeError` about
argument counts from `super()`, "cannot create a consistent method
resolution order", `unhashable type` after adding `__eq__`, `'<' not
supported between instances`, infinite recursion from a `__contains__` that
uses `in` on itself, and an `__iter__` that returns a list instead of an
iterator.

## Security notes

See `security.md`. The essentials: dunder methods run *implicitly*, in
places you will never see in the source — `__repr__` in tracebacks and logs,
`__eq__` and `__hash__` on every dict and set operation — so keep them pure,
cheap, and free of I/O and secrets. Subclassing a third-party class inherits
every method it has, including ones you have not read and ones a future
version may add.

## Extension exercises

1. **Make `Menu` a real sequence.** Inherit from `collections.abc.Sequence`
   and delete your hand-written `__contains__` and `__iter__`. Confirm with a
   run that membership, iteration, `reversed()`, `.index()` and `.count()`
   all still work, then write one sentence on what you traded away (an
   inherited base class) for what you gained (five methods you no longer
   maintain).
2. **Add arithmetic.** Implement `__add__` so two menus concatenate into a
   new one, and `__radd__` so `sum(menus, Menu("empty"))` works. Verify both
   return a *new* object rather than mutating either operand — a `__add__`
   that mutates is a bug every reader will trip over.
3. **Overload the subscript.** Extend `__getitem__` to accept a dish *name*
   as a string key, raising `KeyError` with a helpful message when it is
   missing. Then write a comment explaining why accepting both integers and
   strings in one dunder is a design smell worth thinking twice about.
4. **Inspect the exception in `__exit__`.** Write a second context manager,
   `ServiceLog`, whose `__exit__` reads its three parameters and prints a
   different closing line when the block raised. Prove to yourself that
   returning `True` from it suppresses the error — then change it back.
5. **Drop the inheritance entirely.** Replace the `Station` ABC with a
   `typing.Protocol` marked `runtime_checkable`, delete the base class from
   `GrillStation`, and show with a real `isinstance` result that the class
   still satisfies the interface. You have just moved from nominal typing to
   structural typing without changing a line of behaviour.

## Navigation

- Previous day: Day 067 — Classes and Objects
- Next day: Day 069 — Dataclasses and Type Hints
