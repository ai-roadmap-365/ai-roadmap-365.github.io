# Day 097 lab — Say It Where Someone Will Read It

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Logging and Configuration
- **Day number:** 97 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-097-logging-and-configuration
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-097-logging-and-configuration` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 97 of 365 · Week 14, "Data Formats and Pipelines".

You have a script full of `print`. It works, on your laptop, while you watch
it. Tomorrow it runs at 04:00 on a machine you have no terminal on, and its
output lands in a file that also holds last week's.

By the end of this lab that script says the same things through the `logging`
module, and the difference is measurable rather than stylistic: each line now
carries a severity and a timestamp and a run id, the whole thing can be turned
down without editing a byte of source, the failures arrive with tracebacks
attached, the output parses as JSON so it can be queried, and the API key that
line 3 used to print appears nowhere at all.

Then the other half, which is the same idea pointed the other way. Logging is
how a program tells you what it did; configuration is how you tell it what to
do. You build a four-layer resolver — defaults, then a TOML file, then the
environment, then command-line flags — that records **where every value came
from**, so "why is it doing that?" takes five seconds instead of four files
and a guess. Plus a startup validator, so a bad value fails at 09:00 when
somebody deployed it rather than at 03:00 when the batch reaches it.

Two things in this lab are not what the textbook says, because they were
measured here and the measurement won. Both are marked where they appear.

## Learning objectives

By the end of this lab you will be able to:

- Name the four objects the `logging` module is built from — logger, handler,
  formatter, filter — and say which one does what.
- Diagnose the two-level trap: a logger at DEBUG whose handler is at WARNING,
  and the message that vanishes with no error.
- Reproduce the duplicate-message problem caused by propagation and fix it two
  ways, saying which fix belongs in a library and which in an application.
- Choose between the five levels by asking who the line is for and what they
  do about it.
- Use `exception()` inside an `except` block and state precisely what
  `error(str(e))` throws away.
- Use lazy `%s` formatting and measure what it saves.
- Write a JSON formatter and query the result with nothing but `json` and a
  loop.
- Write a redacting filter, attach it where it actually works, and prove the
  secret appears nowhere in the captured log.
- Configure logging with `dictConfig`, and rotate files with
  `RotatingFileHandler` and `TimedRotatingFileHandler` — while being able to
  argue why stdout plus a supervisor is usually the better answer.
- Resolve configuration through four layers in precedence order, and report
  the provenance of every value.
- Read TOML with `tomllib`, convert environment strings to real types without
  believing that `"false"` is true, and tell a missing variable from an empty
  one.
- Validate configuration at startup with messages that name the setting and
  the layer it came from.
- Keep a secret out of the log, out of the provenance table, out of the
  validation messages and off the command line.

## Prerequisites

- **Day 43** — a working `python3` on your `PATH`. Python 3.11 or newer, for
  `tomllib`.
- **Day 59** — modules, imports and `__name__`, which is exactly what
  `logging.getLogger(__name__)` depends on.
- **Day 65** — JSON, which is what the structured log is made of.
- **Day 66** — exceptions and `try`/`except`, which exercise 4 needs.
- **Day 68** — inheritance, which is how a formatter and a filter are
  extended: you subclass and override one method.
- **Day 69** — dataclasses and type hints, used for `Setting` and `Resolved`.
- **Day 80** — `argparse`, the fourth layer.
- **Day 81** — scheduling and background jobs, where the "log to stdout and
  let the supervisor collect it" argument was first made.
- **Day 84** — the automation toolkit, which is the thing this day's
  configuration resolver was missing.
- **Day 91** — ISO 8601 as a sortable text format, reused here for timestamps.
- **Day 95** — dates, times and time zones, which is why every timestamp here
  is UTC.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64 |
| Linux (any current distribution) | Expected identical, given Python 3.11+ |
| Windows | Use WSL and follow the Linux path. The two shell scripts use `mktemp -d`; native Windows was not tested and no output is claimed for it |

## Hardware requirements

Anything. The largest file this lab writes is a few kilobytes of log, in a
temporary directory, and the whole test suite finishes in about two seconds.
No GPU, no network, no disk to speak of.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | `tomllib` arrived in 3.11; everything else is older |
| `bash` | 3.2 | 3.2.57 | The two harness scripts |

Standard library only: `logging`, `logging.config`, `logging.handlers`, `json`,
`os`, `tomllib`, `argparse`, `pathlib`, `dataclasses`, `random`, `tempfile`.
Check it in one line:

```bash
python3 -c "import tomllib, logging.config, argparse; print('ready')"
```

## Free and open-source options

Everything in this lab is free, and none of it is a download.

- **Python** is under the PSF licence, and this lab uses only its standard
  library. `logging` has been in it since Python 2.3 (2003), `logging.config`
  since the same release, and `tomllib` since 3.11 (2022).
- **`structlog`** (Apache 2.0 / MIT, free) and **`loguru`** (MIT, free) are the
  two best-known third-party logging libraries. **`python-json-logger`** (BSD,
  free) does the JSON formatter you write in exercise 5. Neither `structlog`
  nor `loguru` nor `python-json-logger` is installed on the machine this lab
  was captured on, so the lesson describes all three from their documentation
  and **reproduces no output for them**.
- **`pydantic-settings`** (MIT, free) and **`dynaconf`** (MIT, free) do the
  configuration half. Neither is installed here either, and the same rule
  applies: described, not demonstrated.
- **`python-dotenv`** (BSD, free) is the exception. It happens to be present in
  the system interpreter this lab was captured on, at version 1.2.2, and the
  lesson shows one real run of it — clearly marked as an aside, because the lab
  itself does not use it and does not need it.

No account, no key, no paid tier, and nothing in this lab is degraded without
one.

## Installation

None. Change into this directory and start.

```bash
cd labs/sections/programming-with-python/day-097-logging-and-configuration
python3 --version
```

If your Python lives somewhere unusual, both scripts take an override rather
than guessing:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## File structure

```text
day-097-logging-and-configuration/
├── README.md                        this file
├── metadata.yml                     lab metadata and the recorded run
├── security.md                      secrets, logs, and what this lab does to
│                                    your machine
├── troubleshooting.md               grouped by the symptom you actually see
├── requirements/
│   ├── README.md                    versions, and what is deliberately absent
│   └── requirements.txt             empty of packages, on purpose
├── starter/                         YOUR work happens here
│   ├── 00_brief.md                  the situation, and the twelve exercises
│   ├── 01_logging.py                exercises 1-6
│   ├── 02_config.py                 exercises 7-12
│   └── 03_check.sh                  "N of 12 exercises complete."
├── examples/                        the reference. Read AFTER you have tried
│   ├── applog.py                    JsonFormatter + RedactingFilter, reusable
│   ├── appconfig.py                 the four-layer resolver, reusable
│   ├── config.toml                  layer 2, with no secret in it
│   ├── 01_prints.py                 the script we start from
│   ├── 02_logging_architecture.py   six demonstrations of the confusing parts
│   ├── 03_structured_logging.py     JSON logs, redaction, and its two holes
│   ├── 04_config_resolver.py        four layers, provenance, validation
│   ├── 05_dictconfig_and_rotation.py  dictConfig, rotation, and the honest note
│   ├── 06_run_manifest.py           both halves joined: a reproducible run
│   ├── 07_solution_logging.py       reference answers to exercises 1-6
│   └── 08_solution_config.py        reference answers to exercises 7-12
├── tests/
│   ├── run_tests.sh                 86 checks of real values
│   └── check_exercises.py           the twelve exercise checks, shared with
│                                    starter/03_check.sh
└── expected-output/                 captured from a real run on 2026-08-16
    ├── FIELDS.md                    what must match and what may differ
    ├── prints.txt                   the before picture
    ├── logging-architecture.txt     the six demonstrations
    ├── structured-logging.txt       JSON and redaction
    ├── config-resolver.txt          the four layers
    ├── dictconfig-rotation.txt      dictConfig and rotation
    ├── run-manifest.txt             the reproducible run
    ├── starter-progress.txt         0 of 12 before, 12 of 12 after
    └── test-run.txt                 the full harness run
```

## How to run

```bash
# 1. The whole thing. Start here — it should be green before you change
#    anything, and green again when you have finished.
bash tests/run_tests.sh
echo "exit code: $?"

# 2. Read the brief. starter/00_brief.md

# 3. Find out where you stand. It will say 0 of 12, and say why for each one.
bash starter/03_check.sh

# 4. Now do the work: exercises 1-6 in starter/01_logging.py, 7-12 in
#    starter/02_config.py, re-running step 3 as you go.

# --- everything below is the reference. Look after you have tried. ---

# 5. The script we are starting from. Read its output and count the questions
#    it cannot answer.
python3 examples/01_prints.py

# 6. Six demonstrations of the parts of `logging` that surprise people.
python3 examples/02_logging_architecture.py

# 7. JSON logs, a redacting filter, and the two holes the filter has.
python3 examples/03_structured_logging.py

# 8. Four layers of configuration, and the provenance of every value.
python3 examples/04_config_resolver.py

# 9. dictConfig, file rotation, and why you probably want stdout instead.
python3 examples/05_dictconfig_and_rotation.py

# 10. Both halves joined: a run you can reconstruct from its own log.
APP_API_KEY=sk-live-9f2c4a7b1e63 APP_SEED=7 python3 examples/06_run_manifest.py

# 11. The same run, reproduced from the manifest the previous command printed.
python3 examples/06_run_manifest.py --seed 7 --batch-size 64 \
    --model-name small-encoder --data-version 2026-08-01

# 12. The reference answers, checked by the same checker your work uses.
bash starter/03_check.sh examples/07_solution_logging.py examples/08_solution_config.py
```

## What the commands do

**`bash tests/run_tests.sh`** runs 86 checks of real values. It captures log
output through handlers writing into buffers — never by scraping stdout — and
asserts on parsed structure: how many lines a configuration emitted, which
fields a JSON record carries, which layer supplied which value, whether the
secret is present anywhere. It runs the five demonstration scripts and the
starter checker, and it deliberately breaks one reference answer to prove the
checker can fail. Everything happens in a temporary directory removed by a
`trap`.

**`bash starter/03_check.sh`** imports your two files, calls your functions,
and compares values. It never inspects how you wrote anything, so any correct
implementation passes. Give it two paths to check something else — that is how
the test suite checks the reference answers with the same code.

**`python3 examples/01_prints.py`** is the before picture: a working script
whose every line of commentary is a `print`. Read the output and ask when each
line happened, which run it belongs to, how severe it is, and how you would
turn it down. Then notice line 2.

**`python3 examples/02_logging_architecture.py`** demonstrates, in order: the
converted script at two handler levels; the two-level trap; propagation
producing a duplicate and two fixes for it; `exception()` against
`error(str(e))`; lazy formatting counted; and the five levels with the
question that decides between them.

**`python3 examples/03_structured_logging.py`** builds the JSON formatter,
queries the result with the standard library, then builds the redacting filter
and shows it working on four routes and **failing on a fifth** — a secret
inside an exception message is rendered by the formatter after every filter has
run. Then it shows where the filter must be attached, which is not where you
would expect.

**`python3 examples/04_config_resolver.py`** gives `batch_size` a different
value in all four layers at once and adds them one at a time; prints the
provenance table; demonstrates `bool("false")`; separates a missing environment
variable from an empty one; and validates a deliberately bad configuration.

**`python3 examples/05_dictconfig_and_rotation.py`** configures logging from
one dictionary, sends the same records to a human formatter and a JSON
formatter at two different levels, rotates a file until four generations exist,
performs a `TimedRotatingFileHandler` rollover, and then argues honestly that
you probably want stdout and a supervisor instead.

**`python3 examples/06_run_manifest.py`** resolves configuration, validates it,
logs the manifest as the first event, does three deterministic steps, and
prints how to reproduce itself — from its own log.

## Expected output

The harness ends with a real captured line:

```text
86 checks, 0 failure(s).
```

and exits 0. The starter reports `0 of 12 exercises complete.` with exit 1
before you begin, and `12 of 12 exercises complete.` with exit 0 for the
reference answers.

The two-level trap, from `expected-output/logging-architecture.txt`:

```text
logger level:  DEBUG   (logging.getLogger('trap').level -> DEBUG)
handler level: WARNING (log.handlers[0].level -> WARNING)
--- three calls were made; this is what came out ---
WARNING  trap             this warning gets through
```

Lazy formatting, measured:

```text
1000 suppressed DEBUG calls with %s formatting: 0 renders
1000 suppressed DEBUG calls with an f-string:   1000 renders
```

The four layers, from `expected-output/config-resolver.txt`:

```text
  nothing but the code      batch_size = 32    from default
  + the config file         batch_size = 64    from file:config.toml
  + the environment         batch_size = 128   from env:APP_BATCH_SIZE
  + the flag                batch_size = 256   from flag:--batch-size
```

The provenance table:

```text
setting       value            came from
------------  ---------------  ------------------------
log_level     'DEBUG'          flag:--log-level
batch_size    256              flag:--batch-size
model_name    'small-encoder'  file:config.toml
seed          7                env:APP_SEED
dry_run       False            file:config.toml
data_version  '2026-08-01'     file:config.toml
api_key       ***redacted***   env:APP_API_KEY
```

Startup validation, naming both the setting and the layer:

```text
  3 problems found, all of them at once:
    - log_level: 'VERBOSE' is not one of ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] (from flag:--log-level)
    - batch_size: 0 is below the minimum of 1 (from flag:--batch-size)
    - seed: -1 is below the minimum of 0 (from env:APP_SEED)
```

And the manifest line that makes the run reproducible, with the key absent
from it:

```text
{"ts": "...", "level": "INFO", "logger": "run", "event": "run started", "run_id": "run-4711", "config": {"log_level": "INFO", "batch_size": 64, "model_name": "small-encoder", "seed": 7, "dry_run": false, "data_version": "2026-08-01", "api_key": "***redacted***"}, "provenance": {"log_level": "default", "batch_size": "file:config.toml", "model_name": "file:config.toml", "seed": "env:APP_SEED", "dry_run": "file:config.toml", "data_version": "file:config.toml", "api_key": "env:APP_API_KEY"}}
```

`expected-output/FIELDS.md` says which values must match on any machine and
which are allowed to differ on yours — the timestamps and the traceback line
numbers, mainly.

## Validation steps

1. `bash tests/run_tests.sh` ends with `86 checks, 0 failure(s).` and exits 0.
2. Three logging calls through a DEBUG logger with a WARNING handler produce
   **exactly one** line, and no error is raised for the other two.
3. One call on `myapp.loader`, with a handler on `myapp` and a handler on the
   root, produces **two** lines. Both fixes reduce it to one.
4. `log.error(str(e))` produces one line and **no** traceback;
   `log.exception()` produces a traceback that names both `ValueError` and the
   failing call.
5. 100 suppressed DEBUG calls render the argument **0 times** with `%s` and
   **100 times** with an f-string.
6. Every JSON line parses, and carries `ts`, `level`, `logger`, `event`, the
   static `run_id` and every field passed through `extra=`. `ts` is 24
   characters of ISO 8601 UTC and the values sort chronologically as text.
7. With the redacting filter on the handler, the secret appears **nowhere** in
   the captured log, and the placeholder appears four times — message,
   arguments, nested dict, list.
8. **The measured surprise, one:** with the same filter on the *logger*, a
   record logged on a **child** logger still leaks. Propagation consults the
   ancestors' handlers, not their filters.
9. **The measured surprise, two:** a secret inside an *exception message*
   survives the filter, because the traceback is rendered by the formatter
   after every filter has run. A formatter that scrubs its finished line closes
   it.
10. `batch_size` resolves to **32, 64, 128, 256** as the four layers are added,
    and reports `default`, `file:config.toml`, `env:APP_BATCH_SIZE`,
    `flag:--batch-size`.
11. `APP_MODEL_NAME` unset falls through to the file; set to `""` gives the
    empty string with source `env:APP_MODEL_NAME (set but empty)`; set to a
    value gives the value. Three states, three answers.
12. `APP_DRY_RUN=false` resolves to `False`, and `bool("false")` is `True` —
    both asserted, because the second is why the first needs writing.
13. Startup validation reports **3** problems at once, each naming its setting
    and its provenance, and none containing the secret.
14. `06_run_manifest.py` logs 6 events under one `run_id`, exits 0, prints
    `***redacted***` where the key would be, and produces final loss
    `0.506509` for seed 7 — the same value when re-run from its own manifest.
15. A bad flag stops that program with exit code **2**, before any work, with
    a message naming `batch_size` and `flag:--batch-size`.
16. After the harness finishes, there is no `app.log`, no `daily.log` and no
    `__pycache__` anywhere in the lab directory.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

86 checks, exit 0 when they all pass and non-zero otherwise. They are value
checks: how many lines a configuration produced, what a parsed JSON record
contains, which layer supplied which value, whether a string appears in a
buffer.

Two of them are worth pointing out.

The suite proves the exercise checker is not vacuous. It takes the reference
answer to exercise 4, replaces `logger.exception(...)` with
`logger.error(...)`, runs the checker against the modified copy, and requires
the result to drop to `11 of 12`. A checker that always says 12 is worth
nothing.

And the suite asserts the two surprising findings *as findings* — that a
filter on a logger does not protect records from child loggers, and that a
secret in an exception message survives a filter. If a future Python changes
either behaviour, these tests fail, and the lesson gets corrected rather than
quietly becoming wrong.

Overrides, if your Python is somewhere unusual:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## Cleanup

```bash
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

Both `tests/run_tests.sh` and `starter/03_check.sh` build everything inside
`mktemp -d` and remove it in a `trap`, and `examples/05_dictconfig_and_rotation.py`
does the same unless you give it a directory name. The suite asserts afterwards
that no log file and no `__pycache__` were left in the lab directory, so if you
only ran those there is nothing to clean up.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the symptom you actually
see. The ones you are most likely to meet:

- **Nothing comes out at all** — a logger at DEBUG whose handler is at
  WARNING. Both levels have to pass.
- **Everything comes out twice** — a handler on your logger and a handler on
  the root, and propagation carrying the record past both. `basicConfig` puts
  the second one there.
- **`No handlers could be found`, or a message that vanishes with no
  configuration at all** — no handler anywhere in the chain; the last-resort
  handler emits WARNING and above to stderr and drops the rest.
- **`ValueError: unsupported format character`** — a literal `%` in a message
  that also has `%s` arguments. Double it, or stop using `%` in prose.
- **The redacting filter appears to do nothing** — it is on a logger and the
  record came from a child, or the secret is inside an exception message.
- **`TypeError: File must be opened in binary mode`** — `tomllib.load` needs
  `open(path, "rb")`.
- **`argparse` overrides the environment even when you did not pass the flag**
  — an argparse `default=` was set, so "not passed" and "passed the default"
  became the same thing.

## Security notes

`security.md` has the full account. In short: nothing here opens a socket, runs
`sudo`, needs a credential, or installs anything, and the test suite checks
each of those rather than promising them — including that no URL appears
anywhere in the lab's files.

The string `sk-live-9f2c4a7b1e63` appears throughout this lab and is
**invented**. It is not a credential, it has never been one, and it matches no
real key format closely enough to be mistaken for one. It exists so that the
tests can assert its absence from real captured output.

The day's own security point: **a secret in a log line is an incident, not a
lint failure.** Logs are copied into tickets, screenshots, CI artifacts and
chat messages within minutes of anything going wrong, and every copy has to be
found. The lab therefore keeps the key out of the log, out of the provenance
table, out of the validation messages, and off the command line entirely.

## Extension exercises

1. **Add a `QueueHandler` and find out what it fixes.** The lesson says
   in-process file rotation is racy across processes. The documented answer is
   `logging.handlers.QueueHandler` plus a single listener that owns the file.
   Build it for two worker processes writing one rotating log, and then write
   down what you have actually bought and what you have added — a queue, a
   listener process, and a new way for logs to be lost on shutdown.
2. **Load the `dictConfig` dictionary from the TOML file.** Right now the
   logging configuration is a Python literal and the application configuration
   is a file. Put the first inside the second, and then answer the awkward
   question honestly: how do you log the fact that your logging configuration
   failed to load?
3. **Make the redacting filter catch what it currently misses.** Feed it a
   secret that has been base64-encoded, one that has been split across two
   fields, and one it was never told about. Each of the three fails for a
   different reason. Then decide which of them is worth defending against, and
   what the defence costs on every log line.
4. **Add a fifth configuration layer and place it correctly.** A `.env` file
   sits between the config file and the real environment in most frameworks,
   and secrets-manager values usually sit above the environment. Add both,
   justify the ordering you chose, and update the provenance strings so the
   table still answers the question it exists to answer.
5. **Instrument something real with a run manifest.** Take any script you have
   written in the last three weeks. Give it a run id, a resolved configuration,
   a manifest as its first log line, and JSON on stdout. Then run it twice, a
   week apart, and try to answer "what changed?" from the two logs alone. That
   question is the entire point of the day, and it is the only test that
   matters.

## Navigation

- **Previous day:** Day 96 — Concurrency and async Basics
  (`labs/sections/programming-with-python/day-096-concurrency-and-async-basics/`).
- **Next day:** Day 98 — Section Project: A Complete Data Pipeline
  (`labs/sections/programming-with-python/day-098-section-project-a-complete-data-pipeline/`).
- **Week 14 project:** the week's project directory
  (`labs/sections/programming-with-python/projects/week-14/`), where the
  resolver and the run manifest built here are reused.
