# What every capture in this directory means, and what must match

Four of the five files here are literal captures from a real run on the
authoring machine (macOS 26.5.1, Apple Silicon, Python 3.14.0, Ruff
0.15.22, pytest 9.1.1, bash 3.2.57). This file says which parts of them are
guaranteed on every platform and which are allowed to differ.

## `lint-run.txt` — what the linter finds

Captured by running, from `examples/messy/`:

```bash
pytest -q
ruff check --isolated receipts.py
ruff check --isolated --select E,F,I,B,SIM,UP receipts.py
```

**Guaranteed identical everywhere, on any operating system, with Ruff
0.15.22:** every rule code, every line number, every column number, and
both `Found N errors.` totals. Ruff's analysis is deterministic; it does
not read the clock, the locale, or the filesystem's mood.

| Field | Value | Must match? |
| --- | --- | --- |
| Default selection total | `Found 5 errors.` | Yes |
| Default selection codes | `F401` ×2, `E711` ×2, `F841` | Yes |
| Extended selection total | `Found 10 errors.` | Yes |
| Extended selection codes | `I001`, `F401` ×2, `B006`, `E711` ×2, `F841`, `SIM108`, `UP031`, `E501` | Yes |
| Line and column numbers | `13:8`, `22:42`, `75:89`, … | Yes |
| `E501` measurement | `Line too long (93 > 88)` | Yes |
| `pytest -q` result | `10 passed` | Yes |
| `pytest -q` duration | `in 0.01s` | **No** — timing varies |
| Exit codes | `1` from both `ruff check` runs | Yes |

A **different Ruff version may legitimately differ.** Rules get added,
messages get reworded, and fixes get promoted from unsafe to safe between
releases. That is why `requirements/requirements.txt` pins `0.15.22`. If
your totals differ, check `ruff --version` before assuming anything is
broken.

## `format-diff.txt` — what the formatter would change

Captured with `ruff format --isolated --diff receipts.py`.

**Guaranteed identical everywhere with Ruff 0.15.22:** every hunk. Read the
diff as the specification of what a formatter is allowed to do. Everything
in it is one of: a blank line inserted after the module docstring, a quote
character changed from `'` to `"`, whitespace removed around `=` in a
keyword default, or a call re-wrapped because the single-line form exceeded
88 columns.

**Nothing in that diff changes behaviour.** In particular, notice that
`basket = []` becomes `basket=[]` — the formatter tidies the spacing around
the bug and leaves the bug exactly where it was. That contrast is the point
of the file.

The trailing `1 file would be reformatted` and the exit code `1` are both
guaranteed. `--diff` exits non-zero when it has something to say, which is
what makes it usable in continuous integration.

## `alternatives-run.txt` — the rule families, run one at a time

Captured with four `ruff check --isolated --select <family>` runs plus
`python3 -m tabnanny` and `python3 -m py_compile`.

Guaranteed on every platform: the codes and totals in each of the four Ruff
sections, the silence from `tabnanny` (it prints nothing when indentation
is unambiguous), and the word `parses` from `py_compile`.

The end of the file states plainly which tools were **not** installed on
the capture machine and therefore produced no output anywhere in this lab:
flake8, pylint, Black, isort and pre-commit. Nothing in this lab claims to
show you their output. If you install them, you will see something
different from Ruff, and pylint in particular will find things Ruff does
not.

## `timing.txt` — a measurement, not a benchmark

Captured with `time` around `ruff check` on a temporary directory holding
500 copies of the messy module (38,500 lines of Python), then on a single
file.

| Field | Captured value | Must match? |
| --- | --- | --- |
| File count | 500 | Yes, if you follow the same recipe |
| Total lines | 38,500 | Yes |
| `real` for 500 files | 0.033s, then 0.025s and 0.023s | **No** |
| `real` for one file | 0.013s | **No** |

**These numbers are hardware.** They will differ on your machine, possibly
by a lot, and the first run of any command is slower than the ones after it
because of filesystem caching. Do not quote them as a benchmark; reproduce
them as a measurement. What is robust, and what you should check, is the
*shape*: checking 500 files takes roughly twice as long as checking one,
not five hundred times as long, because process start-up dominates at this
size.

This lab makes no comparative speed claim against any tool it did not run.

## `test-run.txt` — the harness

Captured with `bash tests/run_tests.sh`.

**Guaranteed identical everywhere:** all 37 check labels, in order, all
reporting `ok:`, and the final line `37 checks, 0 failure(s).` with exit
code 0.

The two header lines echo `ruff --version` and `pytest --version` and will
show whatever you installed. If they do not read `ruff 0.15.22` and
`pytest 9.1.1`, some counts inside the run may differ; see the note under
`lint-run.txt`.

One label is worth reading twice:

```text
ok: the unsafe fix changes behaviour, so the test that recorded the bug now fails
```

That check passes when pytest **fails**. It is asserting that an unsafe fix
really is unsafe — that Ruff was right to make it opt-in.

## Platform differences

- **macOS and Linux** — identical in every respect. Ruff ships prebuilt
  wheels for both.
- **Windows** — run the lab under WSL and follow the Linux path. Native
  Windows works too, with `\` path separators in Ruff's output and
  `.venv\Scripts\` instead of `.venv/bin/`; the rule codes, line numbers
  and totals are unchanged. `bash tests/run_tests.sh` needs a bash, so use
  WSL or Git Bash for the harness.
- **Locale** — Ruff's messages are English-only in 0.15.22, so no locale
  setting changes them.
