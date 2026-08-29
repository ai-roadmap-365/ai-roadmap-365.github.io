# Troubleshooting

## `pytest starter` reports passes for exercises you have not written

You ran `pytest examples starter` as a single command. Both directories carry
modules called `acceptance`, `study`, `dataset` and `fixtures`, and that
combined form is unreliable in this repository. Run them as two commands:

```bash
.venv/bin/pytest examples -q
.venv/bin/pytest starter -q
```

A bare `pytest` with no path argument is fine — the two `conftest.py` import
guards handle it, and section 8 of `run_tests.sh` proves the skip count is
unchanged.

## A gate you wrote skips instead of failing

`attempt()` in `test_starter.py` treats both `NotImplementedError` and a
`None` return as "not attempted yet". If your gate falls off the end of a
function without returning, it returns `None` and the test skips. Every path
through a gate must return `_passed(name)` or `_failed(name, findings)`.

## `_failed` raises `ValueError: gate '...' failed without a finding`

That is deliberate. A failing gate with nothing to say is a bug: the reader
learns only that something is wrong, which is exactly the verdict this lab
exists to replace. Collect at least one finding before you fail.

## A finding fails the "does it name something" test

The tests check the text. `test_question_gate_fails_and_names_the_file`
requires every finding to contain `QUESTION.md`;
`test_uncertainty_gate_names_the_sentence` requires the finding to quote the
offending sentence. Copy the exact strings from the docstrings in
`starter/acceptance.py` — they are the strings the tests match against.

## Exercise 5 passes the peeked study

Your gate is almost certainly reading `REPORT.md`. It cannot work: the peeked
study's report, figures, interval and p-value are **byte-identical** to the
honest study's, and `test_confirmation_gate_reads_only_the_log` asserts
exactly that before checking your gate. The peek exists in one place only —
the order of rows in `RESEARCH_LOG.md`. Use `research_log_rows(text)` and
compare the index of the first `confirmation` row against the index of the
row whose activity contains `hypothesis declared`.

## Exercise 8 passes a study whose output moved

You are probably reading the manifest and checking the files exist. The gate
must **recompute** each digest with `sha256_of` and compare it with the
recorded one. Existence is not a checksum.

## Your figures do not hash identically across two runs

Three usual causes, in order of likelihood:

1. Something reads the clock. Any `datetime.now()`, any `strftime` on the
   current time, anywhere in the path from data to output.
2. `metadata={"Software": None}` is missing from `savefig`. Matplotlib writes
   its own version into the PNG's `tEXt` chunk by default, and that tag is
   enough to move the digest between versions.
3. An unseeded `numpy.random` call. `default_rng()` with no seed is a
   different generator every time.

The two PNG digests are still expected to differ **between machines** —
different fonts render different bytes. `expected-output/FIELDS.md` says so,
and nothing in this lab asserts a PNG digest against a stored literal.

## `matplotlib` opens a window, or the run hangs

The lab sets `matplotlib.use("Agg")` before importing `pyplot`, and
`run_tests.sh` also exports `MPLBACKEND=Agg`. If you added your own plotting
code, do the same and never call `plt.show()`. Close figures with
`plt.close(fig)` so a long run does not leak them.

## `ModuleNotFoundError: No module named 'acceptance'`

You are running a script from the lab root instead of from `examples/`. The
scripts import their siblings by plain name, so run them from their own
directory:

```bash
cd examples && ../.venv/bin/python3 01_question_recorded.py && cd ..
```

## `run_tests.sh` says pytest is not found

Create the lab-local virtual environment, or point the suite at an existing
pytest:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
# or
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## A version check fails in section 1

`requirements/requirements.txt` pins the four versions this lab was written
and captured against. If your environment has a different one, the harness
says so rather than pretending the captured numbers still apply. Install the
pinned versions, or accept that `expected-output/` may differ and say so in
your own notes — this course would rather you record a discrepancy than paper
over it.

## `run_tests.sh` reports a file left behind

Section 10 compares `examples/` and `starter/` against an exact inventory. If
it fails, something wrote into the lab directory instead of a temporary one —
most often a study you built by hand while exploring. Delete it and re-run.
The `find … -name __pycache__ …` line in the Cleanup section of `README.md`
clears the other common case.

## You want to see the suite go red

Change `"264"` to `"265"` in the `the delivery carries 264 rows` check in
`tests/run_tests.sh`, run it, and you should see
`81 checks, 1 failure(s).` with a non-zero exit. Change it back. A green suite
you have never watched fail is a suite you have no evidence about.
