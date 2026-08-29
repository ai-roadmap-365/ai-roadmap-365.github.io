# Day 080 lab — A Tool You Would Actually Install

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building CLIs with argparse
- **Day number:** 80 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-080-building-clis-with-argparse
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-080-building-clis-with-argparse` when the site is running.
<!-- generated-links:end -->

## Purpose

On Day 56 you built a command-line tool by reading `sys.argv` yourself. It
worked, and for what it did it was the right choice. This lab starts by
showing you, in eight ordinary command lines, exactly where that approach
stops working — and then builds the thing that replaces it.

You will finish with `notes`: a real multi-subcommand tool with `add`, `list`,
`search`, `export` and `remove`, over a small JSON store. Not a toy. It has
the things users expect and notice the absence of — `-h`, `--help`,
`--version`, short and long option forms, `--` to end option parsing, tab-free
help text organised into groups, sensible exit codes — and the things that
separate a tool from a script: values converted and validated at the parser
rather than three functions later, `--dry-run` on the one destructive command,
results on standard output and diagnostics on standard error so it composes in
a pipeline, a `-` argument that reads the note from standard input, and
configuration that follows the precedence users already expect (flag, then
environment, then default).

The single most useful technique here is **subcommands with
`add_subparsers` and `set_defaults(func=...)`**. It is how git, docker, pip,
and every other tool with more than one verb is structured, and it removes
every `if command == "add"` from your program.

The test suite is unusual and worth reading before you run it: most of it
launches your program as a **subprocess** and inspects what a shell can see —
the exit code, standard output, and standard error, captured to *separate*
files. That is the only honest way to test a command-line interface, and it is
why one check can prove your streams are genuinely separated rather than
merely looking right in a terminal.

## Learning objectives

- Recognise the point at which hand-parsing `sys.argv` starts producing wrong
  answers silently, using a working demonstration rather than an assertion.
- Build an `argparse.ArgumentParser` with `prog`, `description`, `epilog` and
  per-argument `help`, and treat the resulting `--help` output as a
  deliverable rather than a side effect.
- Use `add_subparsers` with `set_defaults(func=...)` so dispatch is
  `args.func(args, streams)` and no branch on the command name exists anywhere.
- Write custom `type=` callables that convert *and* validate, raising
  `argparse.ArgumentTypeError` so a bad value becomes a usage message and
  exit 2 instead of a traceback.
- Use `choices`, `default`, `nargs="+"`, `action="store_true"`,
  `action="append"`, argument groups, and a mutually exclusive group, and say
  what each one buys.
- Separate results (standard output) from diagnostics (standard error), and
  prove the separation with a test that captures the two streams apart.
- Read a note from standard input when the argument is `-`, and detect a
  terminal so the tool explains itself instead of hanging.
- Implement `--dry-run` as a real guarantee — validated for real, written
  never — and verify it by hashing the store before and after.
- Resolve configuration by the expected precedence: flag, then environment,
  then built-in default.
- Make the parser testable by having `parse_args(argv)` take an explicit list,
  and test both in-process and as a subprocess.

## Prerequisites

- The Day 80 lesson.
- Day 56: building a data-driven CLI with `sys.argv` — this lab is its sequel.
- Days 8–14: the command line itself. Pipes, redirection, and exit codes are
  assumed knowledge here.
- Days 64–66: reading and writing files, JSON, and exception strategy.
- Days 71–74: pytest, and Day 74's argument about injecting a boundary rather
  than reaching for it — `parse_args(argv)` and the `Streams` object are that
  idea applied to the command line.
- Day 69: type hints on public functions.
- A text editor, a terminal, and Python 3.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, pytest 9.1.1, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path. On a native Windows console
  substitute `python` for `python3`, and note that the suite's banner contains
  an em dash, so a UTF-8 terminal is needed for it to render. Exit codes,
  stream separation, and the JSON bytes are identical everywhere.

## Hardware requirements

Any computer that runs Python 3. The store this lab writes is a few hundred
bytes; the whole suite finishes in about a second. No special memory, disk,
GPU, or network.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0). The tool itself uses only the
  standard library: `argparse`, `json`, `csv`, `os`, `sys`, `pathlib`,
  `datetime`, `dataclasses`.
- `pytest` for the in-process half of the suite — the only dependency, and
  only for the tests. See [`requirements/README.md`](requirements/README.md).
- `bash` for the test runner (preinstalled on macOS and Linux).

## Free and open-source options

Everything here is free and open source: Python and its standard library,
bash, and pytest (MIT licence). No account, API key, network access, or
purchase is needed at any point.

The lesson's Alternatives section covers the other options for this job —
`click` and `typer`, both free and open source, and `docopt`, which is free
but much less actively maintained. None of them is required here, and the
reason argparse is the right teaching choice is precisely that it needs no
install at all.

## Installation

```bash
cd labs/sections/programming-with-python/day-080-building-clis-with-argparse
python3 --version                                    # confirm Python 3.8+
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

If you already have pytest somewhere, you can skip the virtual environment and
point the runner at it: `PYTEST=/path/to/pytest bash tests/run_tests.sh`.

## File structure

```text
day-080-building-clis-with-argparse/
├── README.md                    ← you are here
├── metadata.yml                 ← machine-readable lab metadata
├── examples/
│   ├── by_hand.py               ← the sys.argv parser, and the 4 of 8 cases it gets wrong
│   └── notes.py                 ← the complete reference tool
├── starter/
│   └── notes.py                 ← YOUR working file: eight numbered exercises
├── tests/
│   ├── run_tests.sh             ← subprocess checks: exit codes and both streams
│   ├── conftest.py              ← puts examples/ or starter/ on sys.path
│   └── test_parser.py           ← in-process checks: parse_args with an explicit list
├── expected-output/
│   ├── sample-run.txt           ← a real captured session
│   ├── help-output.txt          ← every help screen the tool produces
│   ├── test-run.txt             ← a real captured run of the suite
│   └── FIELDS.md                ← the exact contract your tool must satisfy
├── requirements/
│   ├── requirements.txt         ← pytest==9.1.1, for the tests only
│   └── README.md                ← what each dependency is for
├── troubleshooting.md
└── security.md
```

Running the tool writes `notes.json` into whatever directory you run it from,
unless you say otherwise. It is safe to delete at any time.

## How to run

From this directory:

```bash
# 1. See why argparse exists. Eight ordinary command lines, four wrong answers.
python3 examples/by_hand.py

# 2. Read the finished tool's user manual — which it generates itself.
python3 examples/notes.py --help
python3 examples/notes.py add --help

# 3. Drive the reference. Note that --on is explicit, so the output is stable.
python3 examples/notes.py add 'ring the dentist' --tag health --on 2026-03-01 --store notes.json
python3 examples/notes.py add 'argparse turns a script into a tool' -t python -t writing --on 2026-03-02 --store notes.json

# 4. Read a note from a pipe, which is what the '-' convention is for.
echo 'from a pipe' | python3 examples/notes.py add - --tag inbox --on 2026-03-03 --store notes.json

# 5. Results on standard output, so the tool composes.
python3 examples/notes.py list --store notes.json
python3 examples/notes.py list --format json --store notes.json | python3 -m json.tool

# 6. The dry run, and the proof that it wrote nothing.
shasum -a 256 notes.json
python3 examples/notes.py remove 2 --dry-run --store notes.json
shasum -a 256 notes.json

# 7. Three failures, three different exit codes. Check each with `echo $?`.
python3 examples/notes.py add 'x' --on 2026-13-01 --store notes.json ; echo "exit $?"
python3 examples/notes.py frobnicate                                 ; echo "exit $?"
python3 examples/notes.py remove 99 --store notes.json               ; echo "exit $?"

# 8. The stream separation, made visible.
python3 examples/notes.py list --format json -v --store notes.json > result.json 2> chatter.txt
cat result.json
cat chatter.txt

# 9. Your task: exercises 1-8 in starter/notes.py.
python3 starter/notes.py --help

# 10. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/by_hand.py` — runs a hand-rolled `sys.argv` parser against
  eight command lines a user might really type. Three work, one works by luck,
  and four are handled wrongly: `--tag=shopping` silently loses its value, the
  short form `-t` is swallowed as the note text, the typo `--drynrun` is
  accepted and ignored, and a missing option value raises `IndexError`. This
  is the argument for argparse, run rather than asserted.
- `python3 examples/notes.py --help` — prints the tool's manual. Every word of
  it comes from the same `add_argument` calls that do the parsing, which is
  the reason it cannot drift out of date.
- The `add` commands — store two notes with tags and explicit dates. `--on` is
  given explicitly so that every capture in `expected-output/` is reproducible;
  leave it off and the note is filed under today.
- `echo 'from a pipe' | ... add -` — the `-` convention: read the value from
  standard input instead of the command line. This is how a tool joins a
  pipeline, and it is also how you keep a secret out of your shell history.
- `list --format json | python3 -m json.tool` — proves the result on standard
  output is machine-readable, with nothing else mixed into it.
- The two `shasum` calls around `remove --dry-run` — print the same hash. That
  is what makes `--dry-run` a promise rather than a claim.
- The three failing commands — exit 2 (a usage error argparse caught), 2
  again (an unknown subcommand), and 1 (a refusal the tool itself understood).
  Different numbers because a script downstream needs to tell them apart.
- The redirect in step 8 — `result.json` holds valid JSON; `chatter.txt` holds
  `2 note(s) from notes.json`. Two streams, two destinations, no interference.
- `python3 starter/notes.py --help` — fails until exercise 4 is done. That is
  the point: nothing works before the parser exists.
- `bash tests/run_tests.sh` — 76 checks while the starter is unfinished, 133
  once all eight exercises are complete. Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) for the
full captured session and
[`expected-output/help-output.txt`](expected-output/help-output.txt) for every
help screen. The heart of it:

```text
$ python3 notes.py list --store notes.json
ID  DATE        TAGS            TEXT
------------------------------------
 1  2026-03-01  health          ring the dentist
 2  2026-03-02  python,writing  argparse turns a script into a tool
 3  2026-03-03  inbox           from a pipe
exit: 0

$ shasum -a 256 notes.json
c112b7e42cf886f911baa54b62a57b348e501328ddb6ec749f62c5023d70dca0 notes.json

$ python3 notes.py remove 2 --dry-run --store notes.json
would remove note 2
dry run: 1 note(s) would be removed; notes.json was not touched
exit: 0

$ shasum -a 256 notes.json
c112b7e42cf886f911baa54b62a57b348e501328ddb6ec749f62c5023d70dca0 notes.json

$ python3 notes.py add 'x' --on 2026-13-01 --store notes.json
usage: notes add [-h] [--store PATH] [-v | -q] [-t TAG] [--on YYYY-MM-DD]
                 [--dry-run]
                 text
notes add: error: argument --on: '2026-13-01' is not a date in YYYY-MM-DD form (for example 2026-03-01)
exit: 2
```

Every date is supplied explicitly with `--on` and nothing reads the network or
a random number, so these bytes are reproducible on any machine with Python 3.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states the full
contract: every exit code, which stream each kind of output belongs on, the
dry-run guarantee, the precedence rules, and the in-process parser behaviour.

## Validation steps

1. `python3 examples/by_hand.py` ends with
   `8 ordinary command lines, 4 of them handled wrongly.`
2. `python3 examples/notes.py --help` exits 0 and names all five subcommands.
3. `python3 examples/notes.py frobnicate; echo $?` prints `2`, and the message
   appears on standard error — confirm with
   `python3 examples/notes.py frobnicate 2>/dev/null`, which prints nothing.
4. `python3 examples/notes.py add 'x' --on 2026-13-01 >out.txt 2>err.txt`
   leaves `out.txt` **empty** and `err.txt` **non-empty**. Check both. This is
   the single check that proves the streams were separated on purpose.
5. The two `shasum -a 256 notes.json` calls around `remove --dry-run` print
   the identical hash; the one after a real `remove` differs.
6. `python3 examples/notes.py search kangaroo; echo $?` prints `1` and no
   output — grep's convention, not an error.
7. `echo 'x' | python3 examples/notes.py add - --on 2026-03-09 --store t.json`
   exits 0 and the note text really is `x`.
8. Every exercise in `starter/notes.py` is done — `grep -c 'raise
   NotImplementedError' starter/notes.py` returns `0`.
9. `bash tests/run_tests.sh` reports `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `76 checks, 0 failure(s).`
Once all eight exercises are complete the same battery runs a second time
against your file, giving `133 checks, 0 failure(s).` Both are correct; only
the failure count matters. The command exits 0 on success and non-zero on any
failure, so it can run in CI. A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

The suite has two halves, and the split is the lesson:

- **Subprocess checks** launch the real program and inspect exit codes and the
  two streams *separately*. Only a subprocess can observe an exit code, and
  only separate capture can prove stream separation.
- **In-process pytest checks** (`tests/test_parser.py`) call
  `parse_args(["add", "hello"])` and `main(argv, streams)` directly, with
  `io.StringIO` standing in for the terminal. They are far faster, give real
  tracebacks, and can assert on the parsed namespace — which a subprocess can
  never see. They are only possible because `parse_args` takes an explicit
  list and `main` takes its streams as a parameter.

Two checks deserve a look before you run them. The dry-run check is paired
with a **control** that runs the same command *without* `--dry-run` and demands
the hash changes — without it, "the file did not change" would also be
satisfied by a tool that never writes at all. And the suite breaks a copy of
the reference with `sed`, then confirms the help check notices, so you know the
checks are not vacuous.

## Cleanup

The lab writes only `notes.json`, into whatever directory you ran the tool
from, plus `result.json` and `chatter.txt` if you followed step 8:

```bash
rm -f notes.json result.json chatter.txt t.json
```

To reset your work: `git checkout -- starter/`. To remove the virtual
environment: `rm -rf .venv`. The test runner makes its own directory with
`mktemp -d` and removes it in a `trap`, so even a failed run leaves nothing
behind.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: the
`NotImplementedError` from each unfinished exercise, the
`AttributeError: 'Namespace' object has no attribute 'func'` that means a
missing `set_defaults` or a missing `required=True`, the `conflicting option
string: -h` that means a parent parser without `add_help=False`, why
`type=iso_date()` with parentheses is wrong, why a traceback means you raised
`ValueError` instead of `ArgumentTypeError`, why `notes add -` hangs before
exercise 7 is done, why dry-run output can arrive out of order without a
flush, and how to point the suite at an existing pytest.

## Security notes

See [security.md](security.md). Short version: the command line is a trust
boundary, and every `type=` callable is a gate on it — a value that is
converted and validated at the parser can never exist in a dangerous shape
further in. Never build a shell command by string-formatting user input; pass
a list and no shell ever sees it. Secrets do not belong in arguments, because
arguments are visible in the process list and in shell history — which is the
second reason the `-` stdin convention exists. `json.loads` cannot execute
code; `pickle` can. And a `--dry-run` that has never been tested is a claim,
not a guarantee.

## Extension exercises

1. **Add an `edit` subcommand.** It should take an id and either new text as
   an argument or `-` to read from standard input. Count how many places you
   had to touch. If it was more than one `add_parser` block and one handler,
   something in your design is not carrying its weight.
2. **Add a config file.** Read defaults from `~/.notesrc` (a small JSON file)
   and slot it into the precedence chain between the built-in defaults and the
   environment: defaults, then config file, then `$NOTES_STORE`, then the
   flag. Use `parser.set_defaults(**from_config)` — argparse supports exactly
   this, and doing it any other way means writing the precedence logic by hand.
3. **Add shell completion, honestly.** argparse has no built-in completion.
   Write a small bash completion function by hand that offers the five
   subcommand names, and note in a comment which third-party package
   (`argcomplete`) would generate it for you and what that would cost in
   dependencies. Deciding *not* to add a dependency is a real engineering act.
4. **Make the destructive path safer.** Add an interactive confirmation to
   `remove`, plus `--yes` to skip it. Then work out how to test the prompt —
   the answer is that `Streams` already gives you the seam.
5. **Break the streams on purpose.** Change one `streams.stderr.write` in
   `cmd_remove` to `streams.stdout.write` and run the suite. Watch exactly one
   check fail and read its name. Then put it back. Knowing which check catches
   a mistake is worth more than being told the rule.

## Navigation

- **Previous day:** Day 79 — Web Scraping Basics
  (`labs/sections/programming-with-python/day-079-web-scraping-basics/`).
- **Next day:** Day 81 — Scheduling and Background Jobs
  (`labs/sections/programming-with-python/day-081-scheduling-and-background-jobs/`),
  which schedules a tool like this one and needs its exit codes to be right.
- **Week 12 project:** the Personal Automation Toolkit
  (`labs/sections/programming-with-python/projects/week-12/`). The `notes`
  tool is a direct rehearsal for its command-line front end.
