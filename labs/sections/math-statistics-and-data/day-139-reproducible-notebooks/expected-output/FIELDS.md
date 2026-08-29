# What is exact, what may differ, and why

Everything in this directory is captured from a real run on the authoring
machine on 2026-08-20: macOS 26.5.2 (Apple Silicon, arm64), Python
3.14.0, in this lab's own `.venv` built from
`requirements/requirements.txt` (nbformat 5.11.1, nbclient 0.11.0,
nbconvert 7.17.1, ipykernel 7.3.0, pytest 9.1.1).

## Exact everywhere (same code, same input, any machine)

- `scrambled-vs-clean.txt` — the clean run's answer (`30.0`) and the
  scrambled run's answer (`50.0`) are pure arithmetic on Python floats
  and do not depend on the machine. The `execution_count` sequences
  `[1, 2, 3]` and `[1, 3, 2]` are equally exact: they come from counting
  kernel executions, not from timing.
- `markdown-sample.md` — the prose text and the computed value `114` are
  exact; the exact whitespace nbconvert's Markdown template inserts
  around the code fence is a property of the installed `nbconvert`
  version and template, not of the machine.
- `environment-record.txt` — `nbformat`, `nbclient` and `nbconvert`
  version strings are exact **for this lab's pinned versions**; a
  different pin set changes them by design (that is exercise 9's point).
  `python_version` is exact for Python 3.14.0 and will read differently
  under a different interpreter.
- The harness's final line, `16 checks, 0 failure(s)`, and the fail-then-
  restore proof in section 6, are both exact in shape (`M failure(s)`
  where `M` is `0` on green and greater than `0` on a genuinely broken
  suite) — the count of checks (16) is exact for this version of
  `tests/run_tests.sh`.

## Machine-dependent, not asserted to be identical elsewhere

- **The `metadata.execution` timestamps that make two unstripped runs
  differ (exercise 5).** These are wall-clock ISO-8601 strings stamped
  by `nbclient` (`iopub.status.busy`, `iopub.execute_input`,
  `shell.execute_reply`, `iopub.status.idle`). They will never be
  identical across two runs, on this machine or any other, by
  construction — that is the entire point of the exercise, not a gap in
  reproducibility.
- **The `[IPKernelApp] WARNING` line ipykernel prints to stderr** on
  every kernel start, about running over TCP without encryption. It is
  harmless on a local loopback kernel and has been stripped from every
  captured file in this directory; it is real and will appear on your
  terminal too.
- **Wall-clock duration** (`12 passed in 9.78s` in
  `expected-output/examples-run.txt`) will differ machine to machine and
  run to run. Nothing in this lab's tests asserts on timing; every
  assertion is on a value or a shape.

## One honest correction to the day brief

The day brief's framing for the lesson's opening demonstration describes
scrambling a three-cell notebook as "cell 3, then 1, then 3 again." That
exact sequence was tried and does not produce a non-crashing, differing
answer with the cells this lab actually uses: running the third cell
before the first raises `NameError`, because the third cell genuinely
needs a value only the first cell defines. What is built here instead —
run the setup cell, take a look at the report, then add and run a
cleaning step without ever re-running the report — is the same
phenomenon (out-of-order execution silently produces a different, wrong
answer with `execution_count` as the only trace) verified to actually
run without an exception. It is one concrete realisation of the general
claim, not the literal sequence in the brief; see `metadata.yml` for the
full explanation of this call.

## The claim about `execution_count` "revealing" the problem

Exercise 2 and the lesson both say the scrambled notebook's
`execution_count` sequence is non-monotonic and that this is the only
evidence something went wrong. That is checked directly:
`[1, 3, 2]` is not sorted, so `nb_lib.is_monotonic` returns `False`. It
is equally true, and stated in the lesson, that nothing about the
rendered *output* of the notebook looks wrong — cell 2 shows a plain
number, no error, no warning — which is why the rule the day defends is
"restart and run all," not "check the execution counts."
