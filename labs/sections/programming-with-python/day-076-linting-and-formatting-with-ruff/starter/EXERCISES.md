# Exercises — from messy to clean, mechanically

Work through these in order, **from inside this `starter/` directory**:

```bash
cd labs/sections/programming-with-python/day-076-linting-and-formatting-with-ruff/starter
```

Everywhere below, `ruff` and `pytest` mean the ones you installed for this
lab. If you made a lab-local virtual environment, write `../.venv/bin/ruff`
and `../.venv/bin/pytest` instead, or activate the environment first.

The rule this whole exercise is built to prove: **the tools change how the
code reads, not what it does.** The test suite is your evidence. Run it
before, run it after, and watch it stay green.

---

## Exercise 1 — Establish the ground truth

Before changing anything, prove the module works.

```bash
pytest -q
```

You should see `10 passed`. Those ten tests pin every behaviour that
matters: parsing, skipping junk lines, the subtotal, the 20% tax, the
total, the description string, the receipt layout, and — the interesting
one — the fact that `add_item` currently shares a basket between calls.

Read `test_receipts.py`. The last test is labelled as documenting a bug
rather than a feature. Keep that in mind; you will come back to it.

**Write down the exact output line.** It is the number you are protecting.

## Exercise 2 — Look at what the default rule set finds

```bash
ruff check --isolated receipts.py
```

`--isolated` means "ignore any configuration file you might find" — use it
until Exercise 7, so that you are always seeing the rules you asked for and
not rules you inherited from somewhere up the directory tree.

Ruff's default selection is deliberately small: `E4`, `E7`, `E9` and `F`.
Count the findings. Note which of the problems you can see in the file it
did **not** mention.

## Exercise 3 — Ask for more rules

```bash
ruff check --isolated --select E,F,I,B,SIM,UP receipts.py
```

Now you should see **ten** findings across **eight** distinct rule codes.
Write each code down with one sentence in your own words about what it
means. If a code is unfamiliar, ask the tool:

```bash
ruff rule B006
ruff rule F841
```

`ruff rule <code>` prints the rule's full documentation, including why it
exists and what the fix does. It is the fastest way to learn the rule set,
and it needs no network.

Then look at the last line of the output. It tells you how many findings
are fixable safely, and how many more become fixable if you opt in to
unsafe fixes. Those two numbers are the subject of Exercise 5.

## Exercise 4 — Preview the formatter without running it

```bash
ruff format --isolated --diff receipts.py
```

`--diff` prints what the formatter *would* do and changes nothing. Read the
diff carefully. Every single line of it is about appearance: quotes,
spacing around `=` in a default argument, where a long call gets wrapped.
Not one line changes a value, a condition, or a name.

Now run it for real, and then run it again:

```bash
ruff format --isolated receipts.py
ruff format --isolated receipts.py
```

The second run must report `1 file left unchanged`. That property is called
**idempotence**: formatting formatted code is a no-op. It is what makes a
formatter safe to put in a commit hook.

**Re-run the tests: `pytest -q`. Still `10 passed`.** The file looks
different and behaves identically.

## Exercise 5 — Apply the fixes the linter is confident about

```bash
ruff check --isolated --select E,F,I,B,SIM,UP --fix receipts.py
```

Ruff applies only its **safe** fixes: ones it can prove do not change what
the program does and do not throw away a comment. Watch which findings
disappear and which survive.

`pytest -q` — still `10 passed`.

Now look at what is left and read the summary line. The remaining fixes are
marked **unsafe**, which does not mean "wrong" — it means "this fix may
change behaviour, so a human has to say yes." Preview them before applying:

```bash
ruff check --isolated --select E,F,I,B,SIM,UP --diff --unsafe-fixes receipts.py
```

Read that diff and decide, one hunk at a time, whether you agree. Then
apply it:

```bash
ruff check --isolated --select E,F,I,B,SIM,UP --fix --unsafe-fixes receipts.py
ruff format --isolated receipts.py
```

## Exercise 6 — The one the tools could not decide for you

Run the tests again.

```bash
pytest -q
```

This time one test **fails**, and it is the test labelled as documenting a
bug. Read the failure carefully before you do anything else.

What happened: `B006` found a real defect — `basket = []` in the signature
of `add_item` creates one list when the `def` line runs, and every call
that omits `basket` shares it. Two shoppers, one trolley. The unsafe fix
rewrote it to `basket=None` plus an `if basket is None:` guard, which is
the correct shape. Correct code, failing test — because the test was
written to record the broken behaviour.

Your job now is a judgement no tool can make for you:

1. Confirm the new behaviour is the behaviour you want. (It is. Read
   `add_item` and convince yourself.)
2. Rewrite the last test so it asserts the **correct** behaviour: two calls
   that omit `basket` return two independent lists. `assert first is not
   second`, and each list holds exactly one item.
3. Update the test's docstring so it no longer claims to document a bug.
4. `pytest -q` → `10 passed`.

If the unsafe fix did not run for you, make the same change by hand:

```python
def add_item(name, price_cents, basket=None):
    if basket is None:
        basket = []
    ...
```

This is the moment the lab is built around. Nine of the ten findings were
about how the code reads. One was a bug that would have shipped, and the
linter is the only thing in the room that noticed.

## Exercise 7 — Write the configuration

Nobody wants to type `--select E,F,I,B,SIM,UP` forever. Create a file
called `pyproject.toml` **in this `starter/` directory** with at least:

- a `[tool.ruff]` table setting `line-length` and `target-version`;
- a `[tool.ruff.lint]` table with a `select` list naming the rule families
  your project enforces, and an `ignore` list with a **comment explaining
  why** for each entry;
- a `[tool.ruff.lint.per-file-ignores]` table relaxing at least one rule
  for `test_*.py`.

Then check that it works with no flags at all:

```bash
ruff check .
ruff format --check .
pytest -q
```

All three must succeed. `ruff check .` printing `All checks passed!` with
no `--select` in sight means the configuration, not your memory, is now
carrying the rules.

Compare yours with `../examples/clean/pyproject.toml`. It does not have to
match — it has to be *defensible*. Every `ignore` entry you cannot justify
in one sentence is a rule you should either obey or remove from `select`.

## Exercise 8 — Confirm you arrived

```bash
diff -u ../examples/clean/receipts.py receipts.py
```

Differences in the module docstring are expected and fine — the reference
file explains itself. Differences in the *code* are worth reading: either
you found a better answer than the reference, or you missed a step.

Finally, from the lab directory:

```bash
cd .. && bash tests/run_tests.sh
```

## Exercise 9 (optional) — Measure the speed claim yourself

Do not take anybody's benchmark on trust, including this course's. Measure:

```bash
time ruff check --isolated --select E,F,I,B,SIM,UP ../examples/messy/receipts.py
```

Record the `real` figure. It is one small file, so most of what you are
measuring is process start-up — which is exactly the number that decides
whether a tool is tolerable in an editor on every keystroke. Try it again
against a large directory of Python you have lying around and watch how
little the number moves.

## Reset

To start over:

```bash
git checkout -- starter/
```
