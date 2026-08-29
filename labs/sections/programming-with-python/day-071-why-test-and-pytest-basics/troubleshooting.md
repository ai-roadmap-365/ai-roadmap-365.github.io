# Troubleshooting — Day 071 lab

Every symptom below was produced on purpose while building this lab. The
messages are quoted from real runs.

## `pytest: command not found`

pytest is not on your `PATH`. That is normal — a virtual environment keeps it
out of the way deliberately. Either use the lab's copy explicitly:

```bash
.venv/bin/pytest examples
```

or install it first:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

The test runner does not need `pytest` on `PATH` at all; it looks for
`.venv/bin/pytest` inside this lab before it looks anywhere else.

## `FAIL: pytest not found.` from `bash tests/run_tests.sh`

The runner checked three places and found nothing: the `PYTEST` environment
variable, `.venv/bin/pytest`, and `PATH`. Follow the install instructions it
printed, or point it at a pytest you already have:

```bash
PYTEST=/full/path/to/pytest bash tests/run_tests.sh
```

The runner stops here rather than reporting success on nothing. A suite that
skips itself and exits 0 is exactly the failure this lab teaches you to
distrust.

## `no tests ran in 0.00s` and exit code 5

pytest collected nothing. Almost always one of three things:

- you named a path that does not exist, or that contains no `test_*.py` file;
- your test file is not named `test_something.py`;
- your test functions are not named `test_something`.

Check what pytest can see before you debug anything else:

```bash
pytest examples --collect-only -q
```

Exit code 5 is not zero, so a correctly written build script fails on it. A
script that only looks for the word `FAILED` will happily ship.

## `ERROR collecting test_textstats.py` / `import file mismatch`

You ran `pytest starter examples`, or `pytest` with no arguments from the lab
directory. The real message:

```text
import file mismatch:
imported module 'test_textstats' has this __file__ attribute:
  .../starter/test_textstats.py
which is not the same as the test file we want to collect:
  .../examples/test_textstats.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your
test file modules
```

This is worth understanding rather than working around. pytest imports each
test file as a Python module named after the file. Two files called
`test_textstats.py` in two directories both want to be the module
`test_textstats`, and Python keeps exactly one module of a given name in
memory. The lab has two on purpose — a buggy one you are testing and a fixed
reference — so run one directory at a time:

```bash
pytest starter
pytest examples
```

Real projects avoid this by putting an `__init__.py` beside their tests (which
makes the module name include the package path) or by giving every test file a
distinct name. Exit code here is 2: interrupted, not failed.

## `ModuleNotFoundError: No module named 'textstats'`

You ran pytest from inside `starter/` or `examples/`, or from the repository
root. Run it from the lab directory and name the directory as an argument:

```bash
cd labs/sections/programming-with-python/day-071-why-test-and-pytest-basics
pytest starter
```

pytest inserts a test file's own directory at the front of `sys.path` before
importing it, which is what makes the bare `from textstats import ...` at the
top of the test file work. Give it the wrong starting point and the import
fails.

## `ModuleNotFoundError: No module named 'conftest'`

Same cause, same fix. `conftest.py` is imported by pytest automatically, but
`from conftest import SAMPLE` is an ordinary import that needs the directory on
`sys.path` — which pytest arranges only when it is collecting from that
directory.

## `fixture 'sample_text' not found`

Three possibilities:

- you are running from a directory where `conftest.py` is not a parent of the
  test file;
- you renamed or moved `conftest.py`;
- you spelled the parameter differently from the fixture function's name. The
  match is by name and nothing else.

List what pytest can see:

```bash
pytest starter --fixtures | head -40
```

## My test fails and I think it should pass

Read the report from the bottom up. The short test summary names the test; the
`E` lines show both sides of the comparison. For example:

```text
E       assert 4 == 3
E        +  where 4 = add(1, 2)
```

The left value is what your code produced; the right is what you asserted. The
`where` line reconstructs the call that produced it. If the two sides look
identical but the test still fails, you are almost certainly comparing floats —
use `pytest.approx`. Day 70's warning about `0.1 + 0.2` is the same warning.

## Two tests fail and I did not write a bug

Correct. `starter/textstats.py` ships with two real bugs, and exercises 4 and 6
are supposed to catch them. That is the lab. Fix the module in exercise 8.

## `ZeroDivisionError: division by zero`

That is bug 1, in `average_word_length`. Empty text has no words, so
`len(found)` is 0. The docstring says the answer is `0.0`, not a crash.

## Everything passes but I do not believe it

Good. Prove it, the way the test runner does:

```bash
bash examples/vacuous-demo/prove_it.sh
```

Then do it to your own work: break one line of `starter/textstats.py`, run
`pytest starter`, and confirm the run goes red and the exit code is 1. Undo the
break. A suite you have never seen fail is a suite you have never tested.

## `__pycache__` and `.pytest_cache` directories appeared

`__pycache__` is Python's compiled-bytecode cache and is always safe to delete.
`.pytest_cache` is pytest's own; this lab disables it via `addopts =
-p no:cacheprovider` in both `pytest.ini` files, so you should not see one.
To clean up:

```bash
export PYTHONDONTWRITEBYTECODE=1     # prevents it happening again in this shell
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

## The `plugins:` line in my output differs from the captures

Expected. That line lists whatever pytest plugins happen to be installed
alongside pytest. A clean lab `.venv` created from `requirements.txt` shows no
`plugins:` line at all; the authoring machine had two unrelated plugins
present. Nothing in this lab depends on any plugin.

## Colours, or the lack of them

pytest colours its output when it detects a terminal and drops the colour when
output is redirected to a file — which is why the captures in
`expected-output/` are plain. Force it either way with `--color=yes` or
`--color=no`.

## Windows

Use WSL and follow the Linux instructions. Without WSL, the virtual
environment's tools are at `.venv\Scripts\pytest` rather than
`.venv/bin/pytest`, `python` may be spelled `python` rather than `python3`, and
`tests/run_tests.sh` needs a bash — Git Bash or WSL. The pytest commands
themselves are identical.
