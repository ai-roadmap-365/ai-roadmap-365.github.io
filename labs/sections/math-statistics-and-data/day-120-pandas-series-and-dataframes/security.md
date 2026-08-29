# Security notes

## What this lab does to your machine

- Opens **one** network connection, ever: `pip install -r
  requirements/requirements.txt`, to download pandas, pyarrow and NumPy
  from PyPI into this lab's own `.venv`. Every script and test after that
  runs completely offline. `tests/run_tests.sh` section 6 greps every file
  in `examples/` and `starter/` for a URL and fails the suite if it finds
  one, so this is checked rather than merely claimed.
- Writes only inside its own `.venv` directory (created by you, via `python3
  -m venv .venv`) and transient `__pycache__` / `.pytest_cache` directories
  that the test harness removes both before and after every run.
- Never opens a network socket, binds a port, needs `sudo`, or reads or
  writes any file outside this lab's own directory.
- Needs no credential, API key, or account of any kind.

## What the data in this lab is

Every value in every exercise is either a small literal invented for the
demonstration (`[1001, 1002, 1003]`, `["a", "b"]`, the eight-value scores
column) or a synthetic column of 200,000 uniformly random numbers generated
with a fixed seed (`np.random.default_rng(42)`) purely to make the
vectorised-versus-`.apply` timing comparison in exercise 7 meaningful at
scale. Nothing here is real personal, financial or otherwise sensitive
data, and nothing is downloaded from any external dataset.

## The design point this day is actually about

Index alignment is a data-integrity mechanism with a security-adjacent
edge: because two Series with mismatched indexes silently produce `NaN`
rather than an error, a join or arithmetic operation on data collected
under different filtering rules can quietly corrupt a feature column, and
a downstream `fillna(0)` — a completely ordinary, defensible-looking line
— can then bury that corruption where no later check will ever find it
again. This is not a vulnerability the lab exploits; it is the exact
failure mode the lesson and exercise 2 exist to make visible before it
reaches a model or a report.

The Copy-on-Write behaviour in exercise 4 has a related, quieter
implication for code review: a chained-assignment statement that appears
to mutate a DataFrame in place may do nothing at all, which means a
security-relevant filter (`df[df.is_sensitive]['redacted'] = True`) written
in that form can look like it redacted a column while leaving the original
values completely untouched. The `ChainedAssignmentError` warning pandas
3.0.5 raises is the only signal that this happened, and it is easy to miss
if warnings are filtered, redirected, or run in an environment that
discards stderr.
