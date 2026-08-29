# Day 024 lab — Parse and Build JSON

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** JSON and Data Serialization
- **Day number:** 24 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-024-json-and-data-serialization
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-024-json-and-data-serialization` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 24's lesson explains serialization and JSON in depth. This lab makes it
concrete and offline: you validate a valid nested JSON file, extract a nested
field, pretty-print, and watch a deliberately broken file get rejected with a
real parser error — using only `python3`, which is already on your machine.
This is the exact groundwork for Week 4's project, a weather command-line
dashboard that parses live JSON.

## Learning objectives

- Validate a JSON file from the command line and read the pass/fail result.
- Extract a nested field and an array element from a JSON document.
- Pretty-print JSON so a human can read its structure.
- Recognize the error a trailing comma produces and explain why it is invalid.
- Compare the `python3` and `jq` ways of doing the same JSON task.

## Prerequisites

- The Day 24 lesson (read it first — it explains every concept this lab uses).
- A terminal with `python3` available (macOS and Linux ship it).
- No programming experience required; every command is given and explained.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Python 3.14).
- **Linux** — fully supported (any distribution with `python3` and `bash`).
- **Windows** — run the scripts inside WSL, or run the individual `python3`
  commands from the lesson by hand with Python 3 for Windows.

## Hardware requirements

Any computer made in roughly the last 15 years. The lab only reads two small
text files; it needs no special RAM, disk, or GPU.

## Required software

- `python3` (3.x) — for `python3 -m json.tool` and the `json` module.
- `bash` (3.2 or newer) — preinstalled on macOS and Linux.

## Free and open-source options

Everything here is free and open source: `python3`, `bash`, and the optional
`jq` are all open source or ship with your OS. No account, API key, network,
or purchase is needed.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-024-json-and-data-serialization
```

## File structure

```text
day-024-json-and-data-serialization/
├── README.md                          ← you are here
├── metadata.yml                       ← machine-readable lab metadata
├── starter/
│   ├── json_tools.sh                  ← YOUR working file (4 exercises)
│   └── json-worksheet.md              ← record your findings here
├── examples/
│   ├── json_tools.sh                  ← completed reference implementation
│   └── samples/
│       ├── config.json                ← a valid, nested JSON file
│       └── broken.json                ← a deliberately broken JSON file
├── tests/
│   └── run_tests.sh                   ← automated checks (7 checks)
├── expected-output/
│   ├── json_tools.txt                 ← real captured run of the example
│   ├── run_tests.txt                  ← real captured test run
│   └── FIELDS.md                      ← what must hold on every platform
├── requirements/
│   └── README.md                      ← dependency statement (python3 only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/json_tools.sh

# 2. Your task: work through the four exercises in the starter
bash starter/json_tools.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/json_tools.sh` — the reference script. It validates
  `config.json` with `python3 -m json.tool`, extracts `coordinates.lat` and
  `sensors[0]` with `python3` one-liners (showing the `jq` equivalent as a
  comment), counts the top-level keys, pretty-prints the file, and then proves
  `broken.json` is rejected by capturing and printing its real parser error.
- `bash starter/json_tools.sh` — the same four skills as four numbered
  exercises for you to work through: validate, extract a nested field,
  pretty-print, and spot the error in the broken file.
- `bash tests/run_tests.sh` — runs seven checks with no network: `python3`
  is present, the valid sample parses, the broken sample is rejected,
  `coordinates.lat` extracts to `26.9124`, the file has 7 top-level keys,
  `sensors[0]` is `temperature`, and the example script runs end to end.

## Expected output

See [`expected-output/json_tools.txt`](expected-output/json_tools.txt) — a
real captured run. The broken file is rejected with (on Python 3.14):

```text
Illegal trailing comma before end of object: line 4 column 53 (char 97)
```

On Python 3.12 and older the wording is `Expecting property name enclosed in
double quotes` instead — same mistake, same non-zero exit. See
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) for what must hold on
every platform.

## Validation steps

1. Run `bash examples/json_tools.sh` — it must finish without an unexpected
   error and print the broken-file message under step 5.
2. Confirm the extraction prints `26.9124` and nothing else.
3. Confirm the key count is `7`.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `7 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. No network is used.

## Cleanup

Nothing to clean up: the scripts only read the two sample files and write only
console output. To reset your starter work, restore it from git:
`git checkout -- starter/json_tools.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (missing
`python3`, key errors, quoting the one-liner, version-dependent error wording,
optional `jq`).

## Security notes

See [security.md](security.md). Short version: the scripts run no network
calls, need no elevated privileges, and only read local sample files — and the
golden rule of the day is to **parse** untrusted JSON, never to `eval` it.

## Extension exercises

1. Serialize a value you build in Python and confirm the round trip:
   `python3 -c "import json; d={'a':1,'b':[True,None]}; s=json.dumps(d); print(s); print(json.loads(s)==d)"`.
2. Try to serialize a value JSON has no type for, such as a set
   (`python3 -c "import json; print(json.dumps({1,2,3}))"`), read the error,
   and note why sets and dates must be encoded as one of the six JSON types.
3. If you installed `jq`, redo every extraction with `jq` and compare its
   output with the `python3` version.

## Navigation

- **Previous day:** Day 23 — REST Fundamentals: Resources and Verbs
  (`labs/sections/computing-foundations/day-023-rest-fundamentals-resources-and-verbs/`).
- **Next day:** Day 25 — API Authentication: Keys, Tokens, and OAuth
  (`labs/sections/computing-foundations/day-025-api-authentication-keys-tokens-and-oauth/`).
