# Expected output — Day 062 lab

These are real captured runs from the authoring machine (macOS, Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-13). The functions are pure and
deterministic: given the same input they produce the same output and the same
exit codes on every platform Python 3 runs on.

## Files

- `sample-run.txt` — the reference module driven through every subcommand:
  `factorial` (including the base case `factorial(0)` and a rejected
  negative), recursive `sum`, `flatten` of a nested list, `treesum` over a
  nested dict/list tree, `fib` for n = 10 and n = 30 (with call counts), and
  a `python3 -c` import check of `flatten`.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (20 checks, 0 failures). Absolute paths are shown as
  `<repo>`; on your machine they are your real repository path.

## Required behaviour on every platform

A correct module must produce exactly:

| Command | Output (stream) | Exit code |
| --- | --- | --- |
| `factorial --n 5` | `factorial(5) = 120` (stdout) | 0 |
| `factorial --n 0` | `factorial(0) = 1` (stdout) | 0 |
| `factorial --n -3` | `error: factorial is undefined for negative numbers` (stderr) | 1 |
| `sum --values 1,2,3,4,5` | `sum([1, 2, 3, 4, 5]) = 15` (stdout) | 0 |
| `sum --values ""` | `sum([]) = 0` (stdout) | 0 |
| `sum --values 1,x,3` | `error: --values must be comma-separated integers, got '1,x,3'` (stderr) | 1 |
| `flatten --data "[1, [2, [3, 4]], 5]"` | `flatten -> [1, 2, 3, 4, 5]` (stdout) | 0 |
| `flatten --data "[1, 2"` | `error: --data is not valid JSON (...)` (stderr) | 1 |
| `treesum --data '{"a": 1, "b": {"c": 2, "d": [3, 4]}}'` | `treesum -> 10` (stdout) | 0 |
| `fib --n 10` | `fib(10) = 55`, then `naive recursion: 177 calls`, then `memoized (lru_cache): 11 computations, 8 cache hits` (stdout) | 0 |

## The fib call counts (deterministic, machine-independent)

The Fibonacci call counts are fixed mathematics, not timing, so they are the
same everywhere:

| n | fib(n) | naive calls | memoized computations (`misses`) |
| --- | --- | --- | --- |
| 10 | 55 | 177 | 11 |
| 25 | 75025 | 242785 | 26 |
| 30 | 832040 | 2692537 | 31 |

The naive call count is `2 * fib(n + 1) - 1`; the memoized version computes
each of `fib(0)` through `fib(n)` exactly once, so it does `n + 1`
computations. This is why the test asserts a **call-count** reduction (naive
≫ memoized), never a wall-clock time — the ratio is identical on a slow
laptop and a fast server.

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command; the program's own output is identical.
- Passing very deeply nested `--data` (thousands of levels) can raise a
  `RecursionError`; the tool catches it and prints a clear message with exit
  code 1 rather than a traceback. The default recursion limit is about 1000
  frames (see `sys.setrecursionlimit`), and the exact depth at which it
  triggers can vary slightly between Python builds — the message and exit
  code do not.
