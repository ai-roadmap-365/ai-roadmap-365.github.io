# Day 058 lab — Flexible Functions

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Scope, Closures, and *args/**kwargs
- **Day number:** 58 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-058-scope-closures-and-args-kwargs
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-058-scope-closures-and-args-kwargs` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 58's lesson deepens functions with scope, closures, and variadic
arguments. This lab makes those ideas concrete. You build **Flexible
Functions** — a small module with `*args`/`**kwargs` aggregators (`total`,
`average`), two closure factories (`make_counter`, `make_multiplier`) that
capture private, remembered state, and a `**kwargs` configuration merger
(`build_request`) in the exact style ML and LLM libraries use to pass
generation settings. You build it from a starter, one exercise at a time,
then run an automated test suite that imports your functions and proves the
behaviour that matters: captured state persists, two closures stay
independent, keyword-only arguments cannot be passed by position, and caller
`kwargs` override defaults. It rehearses the machinery behind callbacks,
hooks, decorators, and the `model.generate(prompt, **kwargs)` calls you will
make throughout the rest of the course.

## Learning objectives

- Write functions with `*args` that accept any number of positional inputs,
  and `**kwargs` that gather and forward arbitrary named options.
- Define a keyword-only argument (with a bare `*` / after `*args`) so an
  important option must be passed by name.
- Build closures — inner functions that capture enclosing variables — and use
  `nonlocal` to keep private, remembered state (a counter, a factory).
- Merge caller options over defaults with `{**DEFAULTS, **kwargs}`, the ML
  configuration pattern.
- Keep functions testable by taking all input from arguments, and prove a
  closure remembers state and stays independent from another instance.

## Prerequisites

- The Day 58 lesson (read it first — it explains every part this lab builds).
- Day 57: defining functions, parameters and arguments, return values, and
  default arguments.
- Days 50–56: conditionals and loops, lists, dictionaries, comprehensions,
  and building a small program.
- A text editor and a terminal. No experience beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python
  3.14.0).
- **Linux** — fully supported (any distribution with Python 3 and bash).
- **Windows** — use WSL and follow the Linux path, or substitute `python`
  for `python3` if that is how Python is exposed. The module is pure
  standard-library Python and behaves identically everywhere.

## Hardware requirements

Any computer that runs Python 3. The module does no heavy computation and
reads or writes no files; it needs no special memory, disk, or GPU.

## Required software

- `python3` (3.8 or newer; tested on 3.14.0).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only — in fact the module imports nothing; it uses only
  core language features. No packages to install. See
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Everything here is free and open source: Python, bash, and core language
features. No account, API key, network access, or purchase is needed.

## Installation

None beyond Python itself. Move into this directory and you are ready:

```bash
cd labs/sections/programming-with-python/day-058-scope-closures-and-args-kwargs
python3 --version   # confirm Python 3.8+ is available
```

## File structure

```text
day-058-scope-closures-and-args-kwargs/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── flexible.py                 ← YOUR working file (5 numbered exercises)
│   └── functions-worksheet.md      ← design the functions before coding them
├── examples/
│   └── flexible.py                 ← complete reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (functions, demo, starter)
├── expected-output/
│   ├── sample-run.txt              ← real captured demo + import check
│   ├── test-run.txt                ← real captured run of the test suite
│   └── FIELDS.md                   ← required behaviour on every platform
├── requirements/
│   └── README.md                   ← dependency statement (Python 3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory.

```bash
# 1. See the finished module's demo first.
python3 examples/flexible.py

# 2. Import one function and use it on its own (proves it is importable).
python3 -c "import sys; sys.path.insert(0, 'examples'); from flexible import make_counter; c = make_counter(); print(c(), c(), c())"

# 3. Prove two closures keep independent state.
python3 -c "import sys; sys.path.insert(0, 'examples'); from flexible import make_counter; c = make_counter(); d = make_counter(100); print(c(), c(), d(), c())"

# 4. Your task: complete the five exercises in the starter, then run its demo.
python3 starter/flexible.py

# 5. Check your work.
bash tests/run_tests.sh
```

## What the commands do

- `python3 examples/flexible.py` — runs the reference module's `main()` demo,
  printing one call of each function: the variadic `total`, the keyword-only
  `average`, a `make_counter` closure advancing `0 1 2 3`, an independent
  second counter, two `make_multiplier` closures with their own factors, and
  `build_request` filling defaults then honouring an override.
- `python3 -c "...make_counter..."` — imports one function from the module and
  calls it without running the whole demo, which works because the module
  guards its demo behind `if __name__ == "__main__":`.
- The two-counter one-liner — shows that `c` advances `0, 1, 2` while a second
  counter `d` returns `100` in the middle, proving each closure holds its own
  captured `count`.
- `python3 starter/flexible.py` — runs *your* version's demo; once the five
  exercises are complete it matches the reference exactly.
- `bash tests/run_tests.sh` — imports the reference functions and asserts
  their behaviour (variadic sum, keyword-only average, closure state and
  independence, factory capture, kwargs merge and override, and that
  `DEFAULTS` is not mutated), checks the demo output, and checks your starter.
  Exits 0 only if every check passes.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured session:

```text
$ python3 examples/flexible.py
total() -> 0
total(2, 4, 6) -> 12
average(10, 20, 30) -> 20.0
average(1, 2, 3, ndigits=4) -> 2.0
counter: 0 1 2 3
second counter is independent: 100
triple(5) -> 15 ; tenfold(5) -> 50
build_request('hello') -> {'prompt': 'hello', 'temperature': 0.7, 'max_tokens': 256, 'model': 'demo'}
build_request('hello', temperature=0.2) -> temperature=0.2, model=demo
```

The module is deterministic, so your output will match.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the required
value of every call on every platform.

## Validation steps

1. `python3 examples/flexible.py` prints the demo above, including
   `counter: 0 1 2 3` and `second counter is independent: 100`.
2. The two-counter one-liner (command 3 above) prints `0 1 100 2`, proving the
   closures keep independent state.
3. `average(1, 2, 3, ndigits=4)` returns `2.0` and `average(1, 2, 3, 4)`
   returns `2.5` — the `4` is a number, because `ndigits` is keyword-only.
4. `build_request("hello", temperature=0.2)` overrides only `temperature`;
   `model` stays `demo`.
5. Complete the five exercises in `starter/flexible.py`, run its demo, and
   confirm it matches the reference.
6. Run the tests (next section) — every check must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line while the starter is unfinished: `18 checks, 0
failure(s).` Once you complete all five starter exercises, the suite runs
your version through the same strict function and demo checks plus a
`nonlocal` check, giving `30 checks, 0 failure(s).` The command exits 0 on
success and non-zero on any failure, so it can run in CI. A full captured run
is in [`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

The module writes no files, so there is nothing to remove. To reset your work,
restore the starter from git: `git checkout -- starter/flexible.py`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list: `python` vs
`python3`, the `UnboundLocalError` that means a missing `nonlocal`, why two
counters can wrongly advance together, why `ndigits` is keyword-only, merging
`kwargs` in the right order, and importing vs running.

## Security notes

See [security.md](security.md). Short version: the module makes no network
calls, needs no privileges, and reads or writes no files. Its cautionary
lesson is to **forward `**kwargs` deliberately, not blindly** — validate or
allow-list the keys you accept, because a function that passes user-supplied
keyword arguments straight through can expose options that were never meant
to be set.

## Extension exercises

1. Write a minimal `logged` **decorator** (a closure) that wraps any function
   to print its arguments and return value, forwarding with
   `def wrapper(*args, **kwargs):` so it works on `total`, `average`, and
   `build_request` alike.
2. Return *two* closures from one factory — a `next_value` and a `reset` that
   share the same captured `count` via `nonlocal` — and show a reset through
   one is visible through the other.
3. Demonstrate the loop-capture trap: build three functions in a loop that
   should each multiply by their index, show the naive version makes them
   identical, then fix it with a default argument (`lambda n, i=i: n * i`) or
   a `make_multiplier(i)` factory, and explain why in a comment.
4. Add a `summarize(*numbers, **options)` that returns a dict with the count,
   total, and average, letting `options` set `ndigits`, and assert its output.

## Navigation

- **Previous day:** Day 57 — Functions: Definition, Arguments, and Return
  Values
  (`labs/sections/programming-with-python/day-057-functions-definition-arguments-and-return-values/`).
- **Next day:** Day 59 — Modules, Imports, and Project Layout
  (`labs/sections/programming-with-python/day-059-modules-imports-and-project-layout/`, to be written).
- **Week 9 project:** the Flashcard Study App, a spaced-repetition flashcard
  CLI organized into clean modules with documented functions — the closures,
  `**kwargs` configuration, and disciplined scope you practise here are the
  building blocks it stands on.
