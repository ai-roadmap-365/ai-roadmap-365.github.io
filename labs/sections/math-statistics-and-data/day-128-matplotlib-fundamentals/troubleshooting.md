# Troubleshooting

Every entry below was hit while building this lab, or is named by a test
that exists because of it.

## `ModuleNotFoundError: No module named 'plotting'`

You ran a reference script from the lab directory instead of from inside
`examples/`. The scripts import `plotting` from beside themselves.

```bash
cd examples
../.venv/bin/python3 01_the_two_apis.py
cd ..
```

The pytest suites do not have this problem, because pytest puts the test
file's own directory on the import path.

## `ModuleNotFoundError: No module named 'matplotlib'`

You are running the system `python3` rather than the lab's. Everything in
this lab goes through `.venv/bin/python3`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you would rather use an interpreter you already have, the harness
accepts one:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## The starter tests all skip and I have written code

A skip means the function still raises `NotImplementedError`. Replace the
`raise NotImplementedError` line with your own body — leaving it in place
above your code still raises before your return statement is ever reached.

## A window tries to open, or the process hangs

Something imported `matplotlib.pyplot` before `matplotlib.use("Agg")` ran,
or called `plt.show()`. Every file in this lab sets the Agg backend at the
very top, before `import matplotlib.pyplot as plt` — if you add a new
file, keep that order, and never call `plt.show()` anywhere in this lab.
`tests/run_tests.sh` also exports `MPLBACKEND=Agg` as a second line of
defence.

## `AssertionError: expected (600, 400) at 100dpi, got (...)`

Check that `save_at_size_and_dpi` does not pass `bbox_inches='tight'`.
A tight bounding box crops the saved image to the drawn content, which
means the output size is `figsize * dpi` minus whatever margin got
trimmed — not the exact product this exercise is testing. The reference
solution passes no `bbox_inches` at all, which keeps matplotlib's default,
untrimmed canvas.

## My `png_dimensions` function raises or returns the wrong numbers

A PNG file starts with an 8-byte signature (`\x89PNG\r\n\x1a\n`), then its
first chunk, which is always `IHDR`: a 4-byte length, the 4-byte type
string `IHDR`, then width and height as **big-endian** 4-byte unsigned
integers — 24 bytes to read in total, at fixed offsets. A common mistake
is reading the integers as little-endian, which produces a huge, wrong
number rather than a clean error; if your reported dimensions look
absurd (millions of pixels), check the byte order first.

## `ax.get_ylim()` after `set_yscale('log')` still includes zero or a
## negative number

You called `set_yscale('log')` but never forced a redraw. matplotlib
recomputes an Axes' limits from its scale lazily, on the next draw — call
`fig.canvas.draw()` (as the reference solution does) before reading
`ax.get_ylim()`, or the limits you read back may still reflect the
previous linear scale.

## My legend text is in the wrong order, or is empty

`ax.get_legend()` returns `None` until `ax.legend()` has actually been
called — check you called it, and called it after both `ax.plot()` calls
with their `label=` arguments set, not before. The order of
`legend.get_texts()` follows plotting order, so if you plot series B
before series A, the legend will read `[B's label, A's label]` regardless
of what order you intended.

## `plt.get_fignums()` grows across an entire pytest run, not just one test

Every test in `examples/test_reference.py` runs against an `autouse`
fixture that calls `plt.close("all")` before and after each test. If you
add a new test file, add the same fixture (or call `plt.close("all")`
directly) — otherwise figures opened by one test leak into the next
test's `plt.get_fignums()` count, and a genuinely correct implementation
can appear to fail a figure-count assertion that has nothing to do with
its own logic.

## `__pycache__`, `.pytest_cache`, or a stray `.png`/`.svg`/`.pdf` appears
## and section 6 fails

Run the cleanup:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
```

Every image this lab saves goes into a `tempfile.TemporaryDirectory()`
that deletes itself automatically — if a `.png`, `.svg` or `.pdf` file is
found anywhere under the lab directory (outside `.venv`) after a run, it
means a test or script was edited to save somewhere else, and section 6
of the harness will flag exactly that.

Note the `-path ./.venv -prune` in the `__pycache__` cleanup command, and
note that the harness uses the same prune. matplotlib, NumPy and pytest
ship hundreds of their own `__pycache__` directories inside the virtual
environment; those are theirs, not litter you created. `.venv` itself is
the documented setup and is never treated as a stray file.

## Running `pytest` with no arguments gives me a different skip count

It should not, and there is a check for exactly that. Both `examples/`
and `starter/` contain a module called `plotting`. Without the
`conftest.py` in each directory, collecting both suites at once would
import whichever copy was seen first and reuse it for the other — so your
unwritten starter exercises would silently pass against the reference
solution. A wrong answer with a green tick on it is the worst kind of
wrong answer.

If you delete or edit either `conftest.py`, section 4 of the harness will
notice: it compares the skip count from `pytest starter` against the skip
count from `pytest` with no arguments and requires them to be identical.

## Windows

Not run here, and this file will not pretend otherwise. Use the Windows
Subsystem for Linux and follow the Linux instructions, or use Git Bash
with `.venv\Scripts\python.exe` in place of `.venv/bin/python3`. Nothing in
the lab is platform-specific — but "should work" and "was run" are
different claims and only the second one is worth making.
