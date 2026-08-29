# Security notes

This lab computes and prints. It writes no files, opens no connection after the
one-time install, needs no credentials and no `sudo`, and all its data is
invented arithmetic. There is very little attack surface here, so this file
spends most of its length on the three things in the day that genuinely do
matter to code you will write later.

## What the lab does and does not touch

| Concern | Status |
| --- | --- |
| Network | Only `pip install` at setup. Section 7 of `tests/run_tests.sh` greps every source file in `examples/` and `starter/` for `urlopen`, `requests.`, `socket.` and any URL, and fails if one appears. |
| Files written | None outside the lab. The scripts print to stdout; nothing opens a file for writing. |
| Credentials | None. `requires_api_key: false` in `metadata.yml`. |
| Elevated privileges | None. Never run any of this with `sudo`. |
| Personal data | None. Every number is invented and is stated to be invented. |
| Installed packages | Two, pinned exactly, both widely used and both free. `rm -rf .venv` is a complete undo. |
| Code execution from data | None. Nothing here parses, evaluates or deserialises anything. |

The virtual environment lives inside the lab directory, so nothing this lab
installs can affect the rest of your machine.

## The three lessons that do matter beyond this lab

### 1. A numerical method that always returns a number will always return a number

This is the security-relevant idea in the day, and it generalises well past
calculus.

`central_difference(abs, 0.0, 1e-5)` returns `0.0`. There is no derivative
there. Nothing raised, nothing warned, and `0.0` is a *plausible* answer — it is
what you would get at the bottom of a valley. A caller that branches on "the
gradient is zero, so we have converged" would take the wrong branch with
complete confidence.

The general shape: **a function whose failure mode is a plausible value rather
than an exception is a function whose failures are invisible.** When you write
one, give the caller a way to detect the failure. Here the way costs nothing:
the forward and backward differences are already computed, and if they disagree,
the value between them is an average rather than a slope.

### 2. Catastrophic cancellation is a real bug class, not a numerical-analysis curiosity

`f(x + h) - f(x - h)` with a tiny `h` subtracts two nearly equal numbers and
destroys most of the digits they had in common. At h = 1e-300 it destroys all of
them and the answer is exactly zero.

The same arithmetic appears in code that has nothing to do with derivatives:
computing a variance as `E[x²] - E[x]²`, comparing two timestamps stored as
absolute seconds since an epoch, computing a balance as a difference of two
large running totals, solving a quadratic with the standard formula when `b²` is
much larger than `4ac`. In each case the result is quietly less accurate than
its inputs, and in several documented cases that has been enough to make a
comparison, a threshold or an audit come out wrong.

The defence is the same one this lab uses: know which of your intermediate
values are close to each other before you subtract them, and prefer a formula
that does not subtract them at all where one exists.

### 3. A tolerance is a security decision when it gates a comparison

Every float comparison in this lab has a tolerance, and every tolerance is
derived in `examples/dataset.py` from the error terms that actually govern the
method, with the arithmetic written out. None was reached by running a test and
enlarging the number until it went green.

That discipline matters far beyond a maths lab. A tolerance chosen to make a
test pass is a tolerance chosen by whatever bug happened to exist at the time.
When the same habit reaches code that compares a computed signature length, a
retry budget, a rate-limit window or a monetary total, "I widened it until it
stopped complaining" is how a check stops checking. A reference test in this lab
asserts that none of the tolerances is loose enough to be meaningless, which is
a cheap way to keep that honest.

## Reviewing the lab yourself

Everything is plain text and short enough to read in full:

```bash
wc -l examples/*.py starter/*.py tests/run_tests.sh
grep -rn "open(\|write\|urlopen\|socket\|subprocess\|eval\|exec" examples/ starter/
```

The second command finds nothing but the word `write` inside comments and the
`PYTHONDONTWRITEBYTECODE` setting.

## Cleanup

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache
rm -rf .venv
```

That returns your machine to exactly where it was.
