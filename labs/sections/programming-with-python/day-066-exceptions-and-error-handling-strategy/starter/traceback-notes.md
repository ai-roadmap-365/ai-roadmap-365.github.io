# Exercise 0 — read three real tracebacks

Before you write a single handler, produce the failures and read what Python
tells you about them. Run each command from the lab directory and paste the
traceback it prints into the matching box below, then answer the three
questions under it.

The paths in your tracebacks will be **your** absolute paths, not the ones in
`expected-output/tracebacks.txt` — that file has them shortened to `<lab>` so
it stays readable. The exception type, the message, and the order of the
frames are what must match.

```bash
python3 examples/raw_triage.py examples/samples/no-such-file.jsonl
python3 examples/raw_triage.py examples/samples/bad-severity.jsonl
python3 examples/raw_triage.py examples/samples/missing-field.jsonl
```

---

## 1. `FileNotFoundError`

Command: `python3 examples/raw_triage.py examples/samples/no-such-file.jsonl`

```text
paste the traceback here
```

- Which line of `raw_triage.py` actually raised it?
- How many stack frames are shown, and what does that tell you about how
  the program got there?
- Is this an expected condition or a bug in the program?

## 2. `ValueError`

Command: `python3 examples/raw_triage.py examples/samples/bad-severity.jsonl`

```text
paste the traceback here
```

- What exact value could `int()` not convert, and which record was it in?
- Which function is innermost, and why is it printed last?
- Would retrying this call help? Why not?

## 3. `KeyError`

Command: `python3 examples/raw_triage.py examples/samples/missing-field.jsonl`

```text
paste the traceback here
```

- What is the single quoted word after `KeyError:`, and what does it name?
- The file has three records and the first one is fine. What happened to
  the third record, and why?
- Which level of the program is the right place to handle this: the
  expression that raised it, the loop over records, or `main()`? Say why.

---

## 4. What the bare `except` costs

Now run the swallowing version on the same two bad files and record what it
prints and what it exits with:

```bash
python3 examples/swallowing.py examples/samples/no-such-file.jsonl ; echo "exit: $?"
python3 examples/swallowing.py examples/samples/bad-severity.jsonl ; echo "exit: $?"
```

```text
paste both runs here
```

- What number does it print for the missing file, and why is that number
  worse than a crash?
- A script that runs this program every night checks the exit code to decide
  whether to alert someone. What would that script have concluded?
- Write one sentence naming the difference between an *expected condition*
  and a *bug*, using the three tracebacks above as your examples.
