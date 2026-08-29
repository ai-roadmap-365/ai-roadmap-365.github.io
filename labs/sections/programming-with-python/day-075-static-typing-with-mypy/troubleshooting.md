# Troubleshooting — Day 075 lab

Every message below was produced on the authoring machine or is quoted from
mypy's own documentation. If you hit something not listed here, read the error
code in brackets first — it is the searchable part.

## `mypy: command not found` / `pytest: command not found`

The tools are not installed, or not on your `PATH`. Install them into a
lab-local virtual environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Then call them by path (`.venv/bin/mypy`), or activate the environment first.
The test runner searches an explicit override, then `.venv/`, then your
`PATH`, so `bash tests/run_tests.sh` works either way. To point it at
binaries you already have:

```bash
MYPY=/path/to/mypy PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `ModuleNotFoundError: No module named 'catalog'` when running pytest

pytest does not put arbitrary directories on the import path. The lab's
modules live in `starter/` and `examples/`, so tell Python where to look:

```bash
PYTHONPATH=starter .venv/bin/pytest -q starter/test_catalog.py
```

In a real project you would instead have a package directory and an installed
project; that is Day 077's territory.

## mypy reports nothing at all, and the file is clearly wrong

Almost always one of three things.

**The functions have no annotations.** mypy will not check the body of an
unannotated function, because it has nothing to check against. This is gradual
typing behaving exactly as designed, and it is why `Success: no issues found`
on an unannotated codebase means "mypy did not look", not "your code is fine".
Run `mypy --strict` and the same file reports `[no-untyped-def]` for every
function. `starter/untyped_first_run.py` exists to let you see this.

**Something in the path is typed `Any`.** A value of type `Any` can be passed
anywhere and have anything called on it, so checking stops at it and stays
stopped for everything downstream. `starter/any_demo.py` demonstrates this in
one edit.

**You are checking a different file than you think.** mypy takes paths, not
patterns, and follows imports from there. `mypy .` checks the tree from the
current directory.

## `Cannot find implementation or library stub for module named "..."` `[import-untyped]` / `[import-not-found]`

The package you imported ships no type information. Three honest responses, in
order of preference:

1. Install the stubs if they exist. Many popular packages have a companion
   `types-<name>` distribution in typeshed; mypy's message usually names it,
   and `mypy --install-types` will fetch what it can.
2. Check whether the package itself is typed — a package that ships a
   `py.typed` marker file is announcing that its own annotations are usable,
   and you may simply need a newer version.
3. Only if neither applies, silence it for that module specifically, in
   configuration, with a comment saying why:

```toml
[[tool.mypy.overrides]]
module = "some_untyped_dependency.*"
ignore_missing_imports = true
```

Do **not** reach for the global `--ignore-missing-imports` flag as a first
move. It silences the message for every dependency at once, including the ones
that were about to tell you about a real mistake.

## `X | None` raises `TypeError: unsupported operand type(s) for |`

You are on a Python older than 3.10 and evaluating the annotation at runtime.
Either upgrade — this lab requires 3.10 or newer — or add
`from __future__ import annotations` at the top of the file, which makes
Python store annotations as strings instead of evaluating them. The lab's
modules do exactly that.

## My `# type: ignore` did not suppress the error

Check the code in the brackets. An ignore only suppresses the code it names,
and mypy says so explicitly:

```text
error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
note: Error code "union-attr" not covered by "type: ignore[arg-type]" comment
```

That note is the tool being helpful: you guessed a code, and it told you the
right one. Copy the code from the error you actually got. A bare `# type:
ignore` with no brackets suppresses everything on that line, including errors
you have not seen yet — which is why this lab never uses one.

## `Unused "type: ignore" comment` `[unused-ignore]`

You fixed the code and left the ignore behind. Delete the comment. This error
only appears when `warn_unused_ignores` is on, which is why it is on in
`examples/pyproject.toml`: without it, ignore comments quietly outlive the
problems they were added for, and after a year nobody can tell which are still
load-bearing.

## `Returning Any from function declared to return "..."` `[no-any-return]`

Something in the expression you returned is typed `Any` — very often
`json.load`, which is annotated to return `Any` because it genuinely can
return anything. The fix is not to widen the return annotation. Check the
value at the boundary: bind it to a name annotated `object`, narrow it with
`isinstance`, and build the type you promised. `examples/catalog.py`'s
`load_settings` shows the pattern.

## `Function is missing a type annotation` `[no-untyped-def]` on a function I do not want to annotate

Strict mode requires annotations everywhere. That is the point of it, but you
do not have to accept it everywhere at once. Turn it on globally and grant
named exemptions per module, so the exemption list is a visible work queue:

```toml
[[tool.mypy.overrides]]
module = "legacy_importer.*"
disallow_untyped_defs = false
```

## The results look stale

mypy caches analysis in `.mypy_cache/` for speed. If you suspect it is out of
date, delete it or run with `--no-incremental`:

```bash
rm -rf .mypy_cache
.venv/bin/mypy --no-incremental starter/catalog.py
```

The test suite sidesteps the question by using a temporary cache directory it
removes on exit, so it never gives you a stale answer and never leaves a cache
in the lab.

## mypy and my editor disagree

Your editor is probably running a different checker. Visual Studio Code's
Python support uses Pylance, which runs Pyright, not mypy. The two implement
the same specification and agree on the great majority of code, but they are
separate programs with different defaults and they do diverge at the edges.
Pick one as the authority — the one your project's continuous integration runs
— and configure the other to match, rather than chasing both.

## The tests fail after I fix `starter/catalog.py`

Expected, and worth reading carefully. Several checks assert that the **buggy**
starter still produces `[union-attr]` and `[arg-type]`, because proving the
tools disagree is the lesson. Once you have finished the exercises, restore
the original with `git checkout -- starter/` before running the suite, or read
each failure and confirm it is the one you caused on purpose.

## `AttributeError: 'NoneType' object has no attribute 'name'`

You ran the buggy `describe()` with a name that is not in the catalogue. That
is not a problem with the lab — it is the bug, arriving the way it would
arrive in production. mypy told you about it before you ran anything.
