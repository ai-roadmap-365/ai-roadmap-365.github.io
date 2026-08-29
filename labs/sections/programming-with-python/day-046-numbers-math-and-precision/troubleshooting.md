# Troubleshooting — Day 046 lab

## My `== 0.3` check is False and I think that is a bug

It is not a bug — it is the whole point of the lab. In IEEE 754 double
precision, `0.1`, `0.2`, and `0.3` are each stored as the *nearest available*
binary fraction, and `0.1 + 0.2` lands a hair above the stored `0.3`. **Never
compare two computed floats with `==`.** Use `math.isclose(a, b)` (True when
the values are within a small tolerance) or round both sides to the number of
decimals you care about: `round(a, 2) == round(b, 2)`.

## `Decimal("0.1")` is exact but `Decimal(0.1)` is not

This trips up everyone once. `Decimal(0.1)` takes the *float* `0.1` — which is
already the wrong value `0.1000000000000000055...` — and copies that error
into the Decimal. `Decimal("0.1")` parses the **string** "0.1" and stores
exactly one tenth. Rule: **build money Decimals from strings** (or from
integers), never from float literals. Run this to see the difference:

```bash
python3 -c "from decimal import Decimal; print(Decimal(0.1)); print(Decimal('0.1'))"
```

## `python3: command not found`

Your system may expose Python only as `python`. Try `python --version`; if it
reports 3.x, substitute `python` for `python3` in every command. On macOS,
install a current Python from python.org or Homebrew (`brew install python`);
on Debian/Ubuntu, `sudo apt install python3`.

## `SyntaxError` or `IndentationError` in my starter

Python is indentation-sensitive: each statement inside `def main():` must be
indented with the same spaces. If you pasted code, mixed tabs and spaces are
the usual culprit — re-indent with spaces only, or restore the starter from
git (`git checkout -- starter/precision_demo.py`) and edit just the marked
lines.

## `ModuleNotFoundError: No module named 'decimal'` or `'math'`

Both modules are part of the standard library and cannot normally be missing.
This almost always means a file in your working directory is named `math.py`
or `decimal.py` and is shadowing the real module — rename your file and try
again.

## The tests fail on the change section

`tests/run_tests.sh` checks that `725 // 100 == 7` and `725 % 100 == 25`. If
you edited `examples/precision_demo.py`, make sure floor division uses `//`
(two slashes) and not `/` (one slash, which gives `7.25`). Restore the
reference file from git if needed.

## Windows: `bash` is not recognized

Run the tests under WSL, or run the Python program directly with
`python examples\precision_demo.py` (the program itself is pure Python and is
fully cross-platform; only the `.sh` test runner needs a POSIX shell).
