# Troubleshooting — Day 076

## `ruff: command not found` / `pytest: command not found`

You have not installed the dependencies, or you have installed them into a
virtual environment you are not currently using. From the lab directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/ruff --version     # ruff 0.15.22
```

Then either call the tools through `.venv/bin/`, or activate the
environment (`source .venv/bin/activate`), or point the test suite at
tools you already have:

```bash
RUFF=/path/to/ruff PYTEST=/path/to/pytest bash tests/run_tests.sh
```

The suite deliberately stops with this message instead of skipping the
checks it cannot run. A test suite that reports success because it never
executed is worse than no test suite.

## `ruff check` finds nothing, or finds far less than the exercise says

Three usual causes.

**You left out `--select`.** Ruff's default selection is `E4`, `E7`, `E9`
and `F` — a deliberately small set chosen so that adding Ruff to an
existing project is not an instant wall of complaints. `B006`, `I001`,
`SIM108` and `UP031` are all outside it. Exercise 3 uses
`--select E,F,I,B,SIM,UP` for exactly this reason.

**You left out `--isolated`.** Without it, Ruff walks up the directory tree
looking for the nearest `pyproject.toml` or `ruff.toml` and uses whatever
it finds. If you created `starter/pyproject.toml` in Exercise 7 with a
narrow `select`, that file is now in charge. `--isolated` means "use the
built-in defaults and ignore every configuration file", which is what you
want while you are still learning which rule does what.

**You already fixed the file.** `ruff check --fix` edits in place. If you
ran it and then re-ran the exercise expecting the original findings, they
are gone because you removed them. `git checkout -- starter/` restores the
original.

## `ruff check` finds *more* than the exercise says

You are probably on a different Ruff version. Check with `ruff --version`.
Rules are added between releases, and fixes are sometimes promoted from
unsafe to safe. `requirements/requirements.txt` pins `0.15.22`, which is
the version every capture in `expected-output/` came from.

## `ruff format` did not fix my `E501` line

It usually does, by wrapping the call. When it does not, the long thing is
something the formatter is not permitted to break: a single long string
literal, a long URL in a comment, or a long identifier. That is precisely
why the reference `pyproject.toml` puts `E501` in `ignore` with a comment
explaining the reasoning — once a formatter owns line length, the only
`E501` findings left are ones a human would make worse by "fixing".

## `ruff format` reformatted my file and now the tests fail

That should not happen, and if it does, it is worth investigating rather
than shrugging at. Check first that you did not also run `ruff check --fix
--unsafe-fixes` in the same breath — the unsafe fixes are the ones allowed
to change behaviour, and one of them (the `B006` fix) changes it on
purpose. Run the two steps separately and re-run the suite after each to
see which one moved the needle.

## The test in Exercise 6 fails and I do not know why

That failure is the lab working. `test_default_basket_is_shared_between_calls`
was written to assert the **broken** behaviour: `assert first is second`.
Once the mutable default is fixed, two calls get two independent baskets,
so `first is second` is false and the test fails.

The fix is not to revert the code. It is to rewrite the test so it asserts
what you now want to be true:

```python
first = receipts.add_item("apple", 120)
second = receipts.add_item("pear", 95)
assert first is not second
```

A test that fails because you deliberately changed behaviour is a test
doing its job. Compare with `examples/clean/test_receipts.py`.

## `ModuleNotFoundError: No module named 'receipts'`

You ran pytest from the wrong directory. `test_receipts.py` does a plain
`import receipts`, which only works when the module sits beside it and
pytest has put that directory on the import path. `cd` into `starter/`,
`examples/messy/` or `examples/clean/` before running `pytest -q`.

## `ruff check .` behaves differently in `examples/clean/` and `examples/messy/`

It should. `examples/clean/pyproject.toml` exists and `examples/messy/`
has no configuration above it, so the two directories are governed
differently on purpose. Discovering that configuration is per-directory-
tree rather than per-invocation is one of the things the lab is teaching.

## `bash: tests/run_tests.sh: No such file or directory`

Run it from the lab directory, not from `tests/` and not from the
repository root:

```bash
cd labs/sections/programming-with-python/day-076-linting-and-formatting-with-ruff
bash tests/run_tests.sh
```

## The harness leaves directories behind

It should not — every temporary directory it creates with `mktemp -d` is
removed as its check finishes. What *is* left behind is Ruff's own
`.ruff_cache/` and pytest's `__pycache__/`, next to whichever files you
checked. Both are ignored by this repository and safe to delete; the
`## Cleanup` section of the README has the command.

## My `pyproject.toml` is ignored

Ruff reads `[tool.ruff]` from `pyproject.toml`. Two common slips: putting
the settings under a bare `[ruff]` table (wrong — that form belongs in a
standalone `ruff.toml`), and putting `select` directly under `[tool.ruff]`
instead of under `[tool.ruff.lint]`. Confirm what Ruff actually resolved:

```bash
ruff check --show-settings . | head -40
```

## `ruff rule B006` prints nothing useful

Check the spelling and the case — rule codes are upper-case letters
followed by digits, with no space. `ruff rule` needs no network; the
documentation is compiled into the binary.

## Windows

Use WSL and follow the Linux instructions. Native Windows works for `ruff`
and `pytest` themselves — the virtual environment puts them in
`.venv\Scripts\` rather than `.venv/bin/` — but `tests/run_tests.sh` needs
a bash, so run the harness from WSL or Git Bash.
