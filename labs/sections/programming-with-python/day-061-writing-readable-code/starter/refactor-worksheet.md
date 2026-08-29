# Refactor worksheet — turn `messy.py` into readable code

`starter/messy.py` works: it prints a summary of the numbers you pass it. It
is also hard to read — one giant function called `d`, single-letter variables,
no docstrings, no type hints, a bare magic number, and cramped formatting.
Your job is to make it **readable without changing what it does**. The test
suite is your safety net: `bash tests/run_tests.sh` passes now and must keep
passing after every step.

The golden rule of refactoring: **one small change, then run the tests.** If
they still pass, keep going; if they fail, undo that one change and try again.
Never rename and restructure and retype all at once.

## The five steps (do them in order, testing after each)

1. **Rename for meaning.** Give every name a job title. `d` → `main`;
   `a` → the raw argument strings; `l` → `scores`; `t` → a running `total`;
   `m` → `average`; `s` → `ordered`; `md` → `median`; `sd` → `stdev`;
   `p` → the `passing` count; `i` → `score` (or `value`). Run the tests.

2. **Kill the magic number.** The bare `60` is the pass mark. Add a module
   constant near the top — `PASS_MARK = 60.0` — and use it in the comparison.
   Now the number has a name and one place to change. Run the tests.

3. **Decompose into small functions.** Pull each distinct job out of the giant
   function into its own function: `parse_scores`, `mean`, `median`,
   `population_stdev`, `passing_rate`, and a `format_report` that assembles the
   lines. Leave `main` as a short conductor that parses input, handles the
   empty case, and prints the report. Run the tests after each extraction.

4. **Document and type.** Give the module a top docstring (what the file does)
   and each function a one-line docstring that says **why / what it returns**,
   not a play-by-play of the code. Add type hints to every function signature:
   `def mean(scores: list[float]) -> float:`. Run the tests.

5. **Format and (optionally) lint.** Put blank lines between functions, spaces
   around operators (`t=t+i` → `total += score`), and one statement per line.
   If you have them installed, run `black messy.py` to auto-format and
   `ruff check messy.py` (or `flake8`) to catch leftovers; if you do not, the
   suite skips those checks cleanly. Run the tests one last time.

When you are done, `starter/messy.py` should read like
`examples/report.py` — and `bash tests/run_tests.sh` should report 14 checks,
0 failures (plus the readability checks now applied to your starter too).

## Before/after notes (fill these in)

- **Hardest name to choose, and what you picked:**
- **A function you extracted, and the one job it now does:**
- **One comment you deleted because the code already said it, or one you kept
  because it explained *why*:**
- **Did the tests ever go red mid-refactor? What did you change to fix it?**
- **Final test line (`N checks, 0 failure(s), M skipped.`):**
