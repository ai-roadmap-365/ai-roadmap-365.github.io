# Day 076 lab — From messy to clean, mechanically

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Linting and Formatting with Ruff
- **Day number:** 76 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-076-linting-and-formatting-with-ruff
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-076-linting-and-formatting-with-ruff` when the site is running.
<!-- generated-links:end -->

## Purpose

This lab hands you a module that **works**. `receipts.py` prices a small shop
receipt with eight functions, and its ten tests all pass before you touch
anything. It is also written badly on purpose, in eight distinct ways:
unsorted imports, two imports nobody uses, a local variable nobody reads, a
line ninety-three columns wide, two comparisons to `None` written with `==`,
percent-style string formatting made obsolete by newer syntax, an if/else
block that wants to be a ternary — and one mutable default argument that is a
genuine bug rather than a cosmetic complaint.

Your job is to run the tools over it and watch, with evidence, what each one
can and cannot do. The formatter rewrites how the file reads and changes
nothing about what it does — the same ten tests stay green. The linter finds
ten problems across eight rule codes. Its safe autofix clears three of them
and *refuses* to touch the bug. Its unsafe autofix does fix the bug, and then
a test fails — because that test was written to record the broken behaviour.
Deciding what to do about that failure is the one step no tool can take for
you, and it is the moment the lab is built around.

You finish by retiring every command-line flag into a `pyproject.toml` you
write yourself and can defend one entry at a time.

## Learning objectives

- Establish a ground truth with a passing test suite before letting any tool
  edit a file, and use that suite as evidence throughout.
- Read a Ruff finding completely: file, line, column, rule code, message, and
  the `[*]` marker that means a safe fix is available.
- Observe that Ruff's default selection (`E4`, `E7`, `E9`, `F`) finds five
  problems here and misses the only real bug, and widen it deliberately with
  `--select E,F,I,B,SIM,UP` to find ten across eight codes.
- Demonstrate that `ruff format` changes appearance only — the suite stays
  green — and that it is idempotent, by running it twice.
- Demonstrate that formatting fixes no lint findings, by re-linting a
  formatted file and seeing `B006` and `F401` still there.
- Apply safe autofixes, then preview and apply unsafe ones, and articulate why
  the `B006` fix is classified unsafe even though it is correct.
- Make the human decision the unsafe fix forces: confirm the new behaviour,
  rewrite the test that pinned the old behaviour, and get back to green.
- Suppress one rule on one line with `# noqa: F401` and confirm it suppresses
  nothing else.
- Write a `pyproject.toml` with `select`, a justified `ignore`, and a per-file
  ignore, and make `ruff check .` pass with no flags at all.
- Measure Ruff's speed yourself with `time` rather than quoting anybody's
  benchmark, including this course's.

## Prerequisites

- The Day 76 lesson (read it first — it explains the four gates and the
  safe/unsafe distinction this lab proves).
- Day 61: PEP 8, meaningful names, and the readability judgements this lab
  mechanises.
- Days 71–74: pytest, running a suite from the terminal, and reading a test
  failure carefully rather than reacting to it.
- Day 43: `python3 -m venv` and installing a pinned dependency with `pip`.
- Comfort reading a unified diff (`+` and `-` lines with `@@` hunk headers).
- A text editor and a terminal. Nothing beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, Ruff 0.15.22, pytest 9.1.1, bash 3.2.57).
- **Linux** — fully supported. Ruff ships prebuilt wheels for both platforms
  and the output is identical in every respect.
- **Windows** — use WSL and follow the Linux path. Native Windows works for
  `ruff` and `pytest` themselves (the virtual environment puts them in
  `.venv\Scripts\` rather than `.venv/bin/`, and Ruff prints `\` path
  separators), but `tests/run_tests.sh` needs a bash, so run the harness from
  WSL or Git Bash. Rule codes, line numbers and totals are unchanged.

## Hardware requirements

Any computer that runs Python 3. The module under test is 76 lines; the whole
lab is a few hundred lines of Python and text. Ruff's whole-directory run here
takes hundredths of a second. No special memory, disk, or GPU.

## Required software

- `python3` (3.9 or newer; tested on 3.14.0).
- `ruff` **0.15.22** and `pytest` **9.1.1**, both pinned in
  `requirements/requirements.txt`. See
  [`requirements/README.md`](requirements/README.md) for what each is for.
- `bash` for the test runner (preinstalled on macOS and Linux).

## Free and open-source options

Everything in this lab is free and open source, with no account, API key or
paid tier at any point. Ruff and pytest are both distributed under the MIT
licence — Ruff by Astral, pytest by the pytest project. Python, bash and the
standard-library modules the lab also exercises (`ast`, `tomllib`,
`py_compile`, `tabnanny`) cost nothing either.

The lesson's Alternatives section discusses flake8, pylint, Black, isort and
pre-commit — all free and open source too, and **none of them installed on the
machine that captured this lab's output**. That is stated plainly in
[`expected-output/alternatives-run.txt`](expected-output/alternatives-run.txt)
rather than papered over: no output from a tool that was not run appears
anywhere here. If you want the comparison, install them and run them yourself;
that file gives you the exact commands.

## Installation

```bash
cd labs/sections/programming-with-python/day-076-linting-and-formatting-with-ruff
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/ruff --version     # ruff 0.15.22
.venv/bin/pytest --version   # pytest 9.1.1
```

Installing needs the network once. After that the lab runs entirely offline —
neither tool contacts anything, and `ruff rule <code>` prints documentation
compiled into the binary. `.venv/` is already gitignored repo-wide; never
commit it.

If you already have Ruff and pytest elsewhere, you can skip the virtual
environment: the test suite resolves its tools from an explicit environment
variable first, then `.venv/bin/`, then your `PATH`.

## File structure

```text
day-076-linting-and-formatting-with-ruff/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── EXERCISES.md                ← the nine numbered exercises, in order
│   ├── receipts.py                 ← YOUR working file: works, written badly on purpose
│   └── test_receipts.py            ← ten tests pinning current behaviour (one pins the bug)
├── examples/
│   ├── messy/
│   │   ├── receipts.py             ← untouched reference copy of the starting point
│   │   └── test_receipts.py        ← the same ten tests
│   └── clean/
│       ├── receipts.py             ← the destination, after the tools and one human decision
│       ├── test_receipts.py        ← the last test, rewritten to assert correct behaviour
│       └── pyproject.toml          ← reference configuration, every line commented with its reason
├── tests/
│   └── run_tests.sh                ← 37 checks; exits 0 only if all pass
├── expected-output/
│   ├── lint-run.txt                ← real capture: pytest, then both ruff check selections
│   ├── format-diff.txt             ← real capture: ruff format --diff, every hunk
│   ├── alternatives-run.txt        ← real capture: each rule family run separately, plus an honesty note
│   ├── timing.txt                  ← real `time` measurement over 500 files and over one
│   ├── test-run.txt                ← real capture of the harness
│   └── FIELDS.md                   ← what must match everywhere, and what may differ
├── requirements/
│   ├── requirements.txt            ← ruff==0.15.22, pytest==9.1.1
│   └── README.md                   ← what each dependency is for, and the one-time install
├── troubleshooting.md
└── security.md
```

Running the tools also creates `.ruff_cache/` and `__pycache__/` directories
next to the files they touched. Both are gitignored and safe to delete; see
`## Cleanup`.

## How to run

From this directory. Substitute `.venv/bin/ruff` and `.venv/bin/pytest` if you
made a lab-local virtual environment and have not activated it.

```bash
# 1. Read the exercises. They are the spine of the lab.
cat starter/EXERCISES.md

# 2. Establish the ground truth. Ten tests, all passing.
cd starter && pytest -q

# 3. See what Ruff's DEFAULT rule set finds. Note what it misses.
ruff check --isolated receipts.py

# 4. Ask for more rules. Ten findings, eight codes, including the real bug.
ruff check --isolated --select E,F,I,B,SIM,UP receipts.py

# 5. Look up a rule you do not recognise. No network needed.
ruff rule B006

# 6. Preview the formatter, apply it, then apply it again (idempotence).
ruff format --isolated --diff receipts.py
ruff format --isolated receipts.py
ruff format --isolated receipts.py

# 7. Prove it changed nothing that matters.
pytest -q

# 8. Apply the SAFE fixes. Watch B006 survive.
ruff check --isolated --select E,F,I,B,SIM,UP --fix receipts.py
pytest -q

# 9. Preview the UNSAFE fixes, then apply them. A test will fail.
ruff check --isolated --select E,F,I,B,SIM,UP --diff --unsafe-fixes receipts.py
ruff check --isolated --select E,F,I,B,SIM,UP --fix --unsafe-fixes receipts.py
pytest -q

# 10. Exercise 7: write starter/pyproject.toml, then run with no flags at all.
ruff check .
ruff format --check .

# 11. Check everything, from the lab directory.
cd .. && bash tests/run_tests.sh
```

## What the commands do

- `cat starter/EXERCISES.md` — the nine exercises with the exact command for
  each, plus the reset instructions. Work from inside `starter/`.
- `pytest -q` — runs the ten behaviour tests beside `receipts.py`. This is the
  number you are protecting: every tool run below is followed by re-running
  this, and the whole argument of the lab is that it stays at `10 passed`
  until you deliberately change behaviour.
- `ruff check --isolated receipts.py` — the linter with its built-in default
  selection (`E4`, `E7`, `E9`, `F`). `--isolated` means "ignore any
  configuration file you might find above me", which keeps you seeing the
  rules you asked for rather than rules you inherited. Reports five findings
  and, importantly, does **not** report `B006`.
- `ruff check --isolated --select E,F,I,B,SIM,UP receipts.py` — the widened
  selection: pycodestyle, pyflakes, isort, bugbear, simplify and pyupgrade.
  Ten findings across eight codes, one of which is the real defect.
- `ruff rule B006` — prints that rule's full documentation, including a
  "Known problems" section saying when the rule is wrong. Compiled into the
  binary; needs no network.
- `ruff format --isolated --diff receipts.py` — shows what the formatter would
  do and changes nothing. Every hunk is appearance: quotes, spacing around `=`
  in a keyword default, a call re-wrapped because it exceeded 88 columns.
- `ruff format --isolated receipts.py` (twice) — applies it, then proves
  **idempotence**: the second run prints `1 file left unchanged`.
- `ruff check ... --fix` — applies only the fixes Ruff can prove are safe. It
  removes the two unused imports and sorts the import block, and leaves
  `B006`.
- `ruff check ... --diff --unsafe-fixes` then `--fix --unsafe-fixes` — previews
  and then applies the fixes that may change behaviour. One of them does,
  on purpose.
- `ruff check .` and `ruff format --check .` — with your own
  `starter/pyproject.toml` in place, both run with no flags: the configuration
  is now carrying the rules instead of your memory. `--check` is the
  continuous-integration form — it edits nothing and exits non-zero.
- `bash tests/run_tests.sh` — 37 checks proving every claim the lesson makes.
  Exits 0 only if all of them pass.

## Expected output

Four real captures live in [`expected-output/`](expected-output/). The heart of
the lab is [`lint-run.txt`](expected-output/lint-run.txt):

```text
$ pytest -q
..........                                                               [100%]
10 passed in 0.01s

$ ruff check --isolated receipts.py
receipts.py:13:8: F401 [*] `json` imported but unused
receipts.py:14:25: F401 [*] `collections.Counter` imported but unused
receipts.py:29:17: E711 Comparison to `None` should be `cond is None`
receipts.py:36:5: F841 Local variable `skipped` is assigned to but never used
receipts.py:39:20: E711 Comparison to `None` should be `cond is None`
Found 5 errors.
[*] 2 fixable with the `--fix` option (3 hidden fixes can be enabled with the `--unsafe-fixes` option).
exit: 1

$ ruff check --isolated --select E,F,I,B,SIM,UP receipts.py
receipts.py:13:1: I001 [*] Import block is un-sorted or un-formatted
receipts.py:13:8: F401 [*] `json` imported but unused
receipts.py:14:25: F401 [*] `collections.Counter` imported but unused
receipts.py:22:42: B006 Do not use mutable data structures for argument defaults
receipts.py:29:17: E711 Comparison to `None` should be `cond is None`
receipts.py:36:5: F841 Local variable `skipped` is assigned to but never used
receipts.py:39:20: E711 Comparison to `None` should be `cond is None`
receipts.py:65:5: SIM108 Use ternary operator `label = 'found' if hits else 'missing'` instead of `if`-`else`-block
receipts.py:69:12: UP031 Use format specifiers instead of percent format
receipts.py:75:89: E501 Line too long (93 > 88)
Found 10 errors.
[*] 3 fixable with the `--fix` option (5 hidden fixes can be enabled with the `--unsafe-fixes` option).
exit: 1
```

[`format-diff.txt`](expected-output/format-diff.txt) is the whole formatter
diff. Read it as the specification of what a formatter is allowed to do — and
note the hunk where `basket = []` becomes `basket=[]`: the formatter tidying
the spacing around the bug and leaving the bug exactly where it was.

[`alternatives-run.txt`](expected-output/alternatives-run.txt) runs each rule
family separately (`--select E,W`, then `F`, then `I`, then `B`) plus the
standard library's own `tabnanny` and `py_compile`, and ends with a plain
statement of which tools were not installed and therefore produced no output
anywhere in this lab.

[`timing.txt`](expected-output/timing.txt) is a `time` measurement, not a
benchmark: `real 0m0.033s` over 500 copies of the module (38,500 lines) and
`real 0m0.013s` over one file, on the machine described above. Those numbers
are hardware and will differ on yours. What is robust is the shape — five
hundred files cost about twice one file, because process start-up dominates
at this size.

[`FIELDS.md`](expected-output/FIELDS.md) states field by field which parts of
every capture are guaranteed on any platform with Ruff 0.15.22 (all rule
codes, all line and column numbers, both `Found N errors.` totals, all 37
check labels) and which are allowed to differ (pytest's `in 0.01s` duration,
every timing figure).

## Validation steps

1. `pytest -q` in `starter/` reports `10 passed` before you start.
2. `ruff check --isolated receipts.py` reports `Found 5 errors.` and does not
   mention `B006`.
3. `ruff check --isolated --select E,F,I,B,SIM,UP receipts.py` reports
   `Found 10 errors.` across exactly these eight codes: `I001`, `F401`,
   `B006`, `E711`, `F841`, `SIM108`, `UP031`, `E501`.
4. Running `ruff format --isolated receipts.py` a second time prints
   `1 file left unchanged`.
5. `pytest -q` still reports `10 passed` immediately after formatting, and
   again after the safe `--fix`.
6. After the safe `--fix`, re-linting still reports `B006`. That is the tool
   being correct, not failing.
7. After `--fix --unsafe-fixes`, exactly one test fails, and it is
   `test_default_basket_is_shared_between_calls`. You then rewrite it to
   assert `first is not second` and return to `10 passed`.
8. With your own `starter/pyproject.toml`, `ruff check .` prints
   `All checks passed!` with no `--select` anywhere, and `ruff format --check .`
   and `pytest -q` both succeed.
9. Every entry in your `ignore` list carries a comment giving a reason you
   would defend out loud.
10. From the lab directory, `bash tests/run_tests.sh` ends with
    `37 checks, 0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `37 checks, 0 failure(s).` The command exits 0 on
success and non-zero on any failure, so it can run in CI. A full captured run
is in [`expected-output/test-run.txt`](expected-output/test-run.txt).

The suite is worth reading before you run it. It is organised into six
sections, and each proves one claim the lesson makes rather than merely
checking that files exist:

- **Ground truth** — the messy module's pytest suite passes before any tool
  touches it, and the `B006` bug is demonstrated at runtime by calling
  `add_item` twice and asserting the two results are the *same object*.
- **The linter** — `ruff check` exits non-zero, reports each of `I001`,
  `F401`, `B006`, `E711`, `F841`, `SIM108`, `UP031` and `E501` (asserted by
  **rule code**, not by the wording of the message, so a reworded message in a
  future release does not silently break the check), totals exactly 10 under
  the widened selection, and totals 5 without `B006` under the default one.
- **The formatter** — `--check` fails on the messy module and passes on a
  formatted copy; the behaviour suite is still green after formatting; a
  second format run reports `1 file left unchanged`; and re-linting a
  formatted copy still finds `B006` and `F401`, proving formatting fixes no
  lint findings.
- **Autofix** — the safe fix removes `F401` and refuses `B006` and leaves the
  suite green; the unsafe fix does rewrite the mutable default, and then the
  suite **fails**. That last check passes when pytest fails, which is how it
  proves "unsafe" means something.
- **Suppression** — a generated file with `import json  # noqa: F401` has no
  `F401` finding and still has its `E711` finding elsewhere.
- **Configuration and starter** — `ruff check .` and `ruff format --check .`
  both exit 0 inside `examples/clean/` using its own `pyproject.toml`; the
  cleaned module passes the same behaviour suite and no longer shares a
  basket; both modules agree on every price, description and receipt line;
  `S101` fires on the test file with `--isolated` and is silent with the
  per-file ignore in force; the reference `pyproject.toml` parses and declares
  what it claims to; and your `starter/receipts.py` is still valid Python with
  all eight public functions and a passing suite.

Every temporary directory the harness makes with `mktemp -d` is removed as its
check finishes.

## Cleanup

The lab writes nothing outside its own directory except temporary directories
under your system temp path, which the harness removes itself. What is left
behind is tool cache:

```bash
find . -type d -name ".ruff_cache" -prune -exec rm -rf -- {} +
find . -type d -name ".pytest_cache" -prune -exec rm -rf -- {} +
find . -type d -name "__pycache__" -prune -exec rm -rf -- {} +
```

To reset your work, restore the starter from git: `git checkout -- starter/`.
To remove the virtual environment entirely, `rm -rf .venv`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `ruff:
command not found`, the three reasons `ruff check` finds fewer findings than
the exercise says (missing `--select`, missing `--isolated`, or you already
ran `--fix`), why a different Ruff version legitimately finds more, why
`ruff format` sometimes cannot fix an `E501`, what to do when the test in
Exercise 6 fails (nothing — that failure is the lab working),
`ModuleNotFoundError: No module named 'receipts'`, why `ruff check .` behaves
differently in `examples/clean/` and `examples/messy/`, the two ways a
`pyproject.toml` gets silently ignored, and the Windows path.

## Security notes

See [security.md](security.md). Short version: a linter is a security control
and not as a metaphor. The `S` family flags patterns with a breach history —
`shell=True`, unsafe YAML loading, `pickle` on untrusted input, hard-coded
passwords — and the `B` family catches correctness traps that become security
bugs. `B006`, this lab's own bug, is the clearest case: in `add_item` a
mutable default means two shoppers share a trolley, and in
`def handler(request, cache={})` in a web application the identical defect
leaks one user's data into the next user's response. The file also covers why
`S101` is relaxed for tests and only for tests, why a bare `# noqa` is an
unauditable blind spot that hides security rules too, and the one real risk in
`pre-commit`: it downloads and executes the hook repositories you name, so pin
them to a revision and read what you are pinning.

## Extension exercises

1. **Build a minimal linter from first principles.** Using only the standard
   library and `ast.parse`, write a script that reports every module-level
   import whose name never appears again (your own `F401`) and every function
   argument whose default is a list, dict or set literal (your own `B006`),
   printed as `path:line:col: X001 message`, exiting 1 on findings. Run it on
   `examples/messy/receipts.py` and compare line numbers with Ruff's real
   output. Then find the first case yours gets wrong — an import used only
   inside an f-string, or only in an annotation — and appreciate how much of a
   mature rule is edge cases.
2. **Measure, do not quote.** Follow Exercise 9 in `starter/EXERCISES.md` to
   `time` a run over one file and over 500 copies, then over the largest
   directory of Python you have. Write down files-per-second at all three
   sizes and describe in two sentences where process start-up stops
   dominating. Report your hardware; do not repeat this lab's figures.
3. **Add a rule family and pay for it.** Add `N` (naming) and `D` (docstrings)
   to `examples/clean/pyproject.toml` and re-run `ruff check .`. Count the new
   findings. Decide, for each, whether you would fix it, suppress it with a
   reason, or drop the family — and write the reason as a comment in the
   configuration. This is the judgement half of the lesson, in one file.
4. **Break the suppression on purpose.** In `examples/clean/receipts.py`, add
   an unused import with a bare `# noqa`, then with `# noqa: F401`, then with
   `# noqa: E501`. Predict what `ruff check .` reports each time before you
   run it. Then enable `RUF100` and watch it flag the suppression that is no
   longer suppressing anything.
5. **Write the CI job.** Without installing anything, write the three-command
   shell script a continuous-integration system would run over this lab —
   `ruff format --check .`, `ruff check --no-fix .`, `pytest -q` — and explain
   in one sentence each why `--check` and `--no-fix` are the right forms there
   and the wrong forms at your desk.

## Navigation

- **Previous day:** Day 75 — Type Checking with mypy
  (`labs/sections/programming-with-python/day-075-type-checking-with-mypy/`).
  Yesterday's gate proves the type claims; today's proves nothing about types
  and catches an entirely different class of defect.
- **Next day:** Day 77 — the last day of Week 11, which assembles the gates
  into one workflow (`labs/sections/programming-with-python/`).
- **Predecessor lesson:** Day 61 — Writing Readable Code
  (`labs/sections/programming-with-python/day-061-writing-readable-code/`).
  Every judgement you made by hand there is a rule code here.
- **Week 11 project:** the Tested Utility Library
  (`labs/sections/programming-with-python/projects/week-11/`), where the
  configuration you write in Exercise 7 becomes the project's real gate.
