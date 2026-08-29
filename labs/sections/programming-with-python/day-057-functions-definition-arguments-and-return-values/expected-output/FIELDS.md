# Expected output — Day 057 lab

These are real captured runs from the authoring machine (macOS, Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-13). Every function in the library
is **pure and deterministic**: given the same arguments it returns the same
value on every platform Python 3 runs on, so your output will match.

## Files

- `sample-run.txt` — the output of `python3 examples/demo.py`, which imports
  the library and *uses* what each function returns: composing calls,
  unpacking a returned tuple, and passing keyword arguments.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (30 checks, 0 failures). Absolute paths are shown as
  `<repo>`; on your machine they are your real repository path.

## Required behaviour on every platform

A correct library must return exactly these values:

| Call | Returns |
| --- | --- |
| `word_count("the quick brown fox")` | `4` |
| `word_count("   ")` | `0` |
| `normalize_whitespace("  a   b  ")` | `'a b'` |
| `reverse_words("one two three")` | `'three two one'` |
| `is_palindrome("A man, a plan, a canal: Panama")` | `True` |
| `celsius_to_fahrenheit(100)` | `212.0` |
| `clamp(1.5)` | `1.0` (default range `[0.0, 1.0]`) |
| `clamp(-3, low=-10, high=10)` | `-3` |
| `mean([2, 4, 6])` | `4.0` |
| `summarize([2, 4, 6])` | `(3, 12, 2, 6, 4.0)` (a tuple) |
| `greet("Ada")` | `'Hello, Ada!'` |
| `greet("Grace", greeting="Welcome", punctuation=".")` | `'Welcome, Grace.'` |
| `tally(["a", "b", "a"])` | `{'a': 2, 'b': 1}` |
| `tally(["a"], {"a": 5})` | `{'a': 6}` |

## Required errors

| Call | Result |
| --- | --- |
| `mean([])` | raises `ValueError` (mean of nothing is undefined) |
| `summarize([])` | raises `ValueError` (cannot summarize an empty sequence) |
| `clamp(5, low=10, high=0)` | raises `ValueError` (low greater than high) |

## Purity guarantees the tests check

- **Repeatable:** calling any function twice with the same arguments returns
  equal results.
- **No leaked state:** `tally` uses a `None` default (not `{}`), so a second
  call never remembers items from a first — the mutable-default trap is
  avoided.
- **No mutation of inputs:** `summarize([3, 1, 2])` leaves the list `[3, 1, 2]`
  unchanged; `tally(items, start)` does not mutate `start`.

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before the demo command; the program's own output is identical.
- `2 + 2 == 4.0` and other float results print the same on CPython 3.8–3.14.
  `celsius_to_fahrenheit` returns a float (because of the `/ 5`), so `212.0`,
  not `212`, is correct.
- No files are written, no network is used, and no temporary state is left
  behind — the tests import the module and assert on return values only.
