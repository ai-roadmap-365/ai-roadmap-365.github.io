# Types worksheet — Day 044

Fill this in using the Python REPL (start it with `python3`). Verify every
answer live rather than from memory, and paste the REPL lines that prove each
claim. Keep this worksheet — the next lesson on strings builds on it.

## 1. The type of three values

Choose three values of three *different* types. For each, run `type(value)`
in the REPL and record the result.

| Value you tested | `type(value)` reports | Type name |
| ---------------- | --------------------- | --------- |
| _e.g._ `42`      |                       |           |
|                  |                       |           |
|                  |                       |           |

Paste your REPL lines here:

```text
(paste, e.g.)
>>> type(42)
<class 'int'>
```

## 2. Is a string mutable?

Answer in one sentence: **is a `str` mutable or immutable?**

> Your answer:

Now prove it with `id()`. Record `id(s)` before and after "changing" a
string, and say whether the id stayed the same or changed, and what that
tells you.

```text
(paste your REPL session, e.g.)
>>> s = "cat"
>>> id(s)
...
>>> s = s + "s"
>>> id(s)
...
```

> What the ids show:

## 3. A conversion that fails

Find one type conversion that raises an error. Record exactly what you
converted, the exact error message, and *why* it fails (in terms of this
lesson).

- **What you converted:** _e.g._ `int("3.5")`
- **Exact error:**
- **Why it fails:**

```text
(paste your REPL line and the traceback)
```

## Check

- [ ] Every row of section 1 is filled with a real REPL result.
- [ ] Section 2 states mutable/immutable correctly and cites id() evidence.
- [ ] Section 3 shows a real conversion error with an explanation.
