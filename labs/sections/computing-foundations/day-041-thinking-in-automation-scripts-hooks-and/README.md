# Day 041 lab — A Real Pre-Commit Hook

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Thinking in Automation: Scripts, Hooks, and Pipelines
- **Day number:** 41 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-041-thinking-in-automation-scripts-hooks-and
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-041-thinking-in-automation-scripts-hooks-and` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 41's lesson is about the automation mindset — scripts, hooks, and pipelines.
This lab makes it real. You install a working git `pre-commit` hook, watch it
**block a bad commit** and **allow a clean one**, and run a tiny **fail-fast
pipeline** that stops at the first failing stage. Everything runs offline in a
throwaway repository the scripts create and delete for you, so you can experiment
without touching any real project.

## Learning objectives

- Install a git `pre-commit` hook and explain why it must be executable.
- Watch a hook reject a commit (non-zero exit) and allow a clean one (zero exit).
- Read a hook and point to the line that aborts a commit.
- Run a pipeline of ordered stages and observe fail-fast behavior.
- Complete four exercises that build a hook check and extend a pipeline.

## Prerequisites

- The Day 41 lesson (read it first — it explains hooks, pipelines, and fail-fast).
- Basic git from Week 5: staging and committing.
- A terminal with `git` and `bash` (macOS, Linux, or WSL on Windows).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with git and bash).
- **Windows** — use WSL (Windows Subsystem for Linux) and follow the Linux path; native PowerShell is not supported for this lab.

## Hardware requirements

Any computer that runs git. The scripts create tiny temporary repositories and
need no meaningful RAM, disk, or GPU.

## Required software

- `git` (any recent version — check with `git --version`).
- `bash` 3.2 or newer (preinstalled on macOS and Linux).
- Standard utilities: `mktemp`, `grep`, `printf`, `chmod` — all part of the base system.

## Free and open-source options

Everything here is free and open source: git and bash ship with or install freely
on every supported OS. No account, API key, network, or purchase is needed. The
lesson surveys free tools you can grow into — the pre-commit framework, hosted CI
free tiers, and Makefiles — but this lab needs none of them.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-041-thinking-in-automation-scripts-hooks-and
```

## File structure

```text
day-041-thinking-in-automation-scripts-hooks-and/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── hook_demo.sh                ← YOUR working file (4 exercises)
│   └── automation-worksheet.md     ← worksheet for the practice assignment
├── examples/
│   ├── pre-commit                  ← the reference hook (installed by the demo and tests)
│   ├── hook_demo.sh                ← full reference walkthrough
│   └── pipeline.sh                 ← the tiny fail-fast pipeline
├── tests/
│   └── run_tests.sh                ← automated checks (real behavior)
├── expected-output/
│   ├── demo-output.txt             ← real captured demo run (macOS)
│   ├── tests-output.txt            ← real captured test run (macOS)
│   └── FIELDS.md                   ← what a correct run must show, all platforms
├── requirements/
│   └── README.md                   ← dependency statement (git + bash only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the whole thing work end to end (blocks bad, allows clean, runs pipeline)
bash examples/hook_demo.sh

# 2. Watch the pipeline: first all green, then forced to fail fast at 'test'
bash examples/pipeline.sh
bash examples/pipeline.sh test

# 3. Your task: complete the four exercises in the starter, then run it
bash starter/hook_demo.sh

# 4. Check everything
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/hook_demo.sh` — creates a temporary git repo, installs
  `examples/pre-commit`, attempts a commit of a file with trailing whitespace
  (rejected), fixes it and commits cleanly (allowed), then runs the pipeline
  green and failing, and deletes the temp repo on exit.
- `bash examples/pipeline.sh` — runs the stages lint, test, build, deploy in
  order; with no argument all pass (exit 0). Pass a stage name
  (`bash examples/pipeline.sh test`) to make that stage fail and see the pipeline
  stop before the later stages (exit 1) — failing fast.
- `bash starter/hook_demo.sh` — the same idea as a skeleton with four numbered
  exercises: complete a hook check, block a bad commit, commit clean, and add a
  pipeline stage.
- `bash tests/run_tests.sh` — installs the hook in a fresh temp repo and verifies
  real behavior: the hook blocks trailing whitespace and a syntax error, allows a
  clean commit, and the pipeline fails fast while succeeding when all stages pass.

## Expected output

See [`expected-output/demo-output.txt`](expected-output/demo-output.txt) and
[`expected-output/tests-output.txt`](expected-output/tests-output.txt) — real
captured runs. The demo's two key lines are:

```text
Result: the hook BLOCKED the bad commit (exit non-zero), as intended.
Result: the hook ALLOWED the clean commit.
```

Your temporary paths will differ; the shape must match.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists exactly what a
correct run must show on every platform.

## Validation steps

1. Run `bash examples/hook_demo.sh` — confirm you see both the BLOCKED and ALLOWED results.
2. Run `bash examples/pipeline.sh` — it must print all four stages and exit 0.
3. Run `bash examples/pipeline.sh test` — it must stop at `test`, never print `build` or `deploy`, and exit non-zero.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `6 checks, 0 failure(s).` The command exits 0 on success and
non-zero on any failure, so it runs unchanged in CI.

## Cleanup

Nothing to clean up. Every script does its work inside a temporary directory
(`mktemp -d`) and deletes it on exit, leaving your machine untouched. To reset the
starter file to its original state, restore it from git:
`git checkout -- starter/hook_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (hook not
executable, `--no-verify`, missing git, invisible trailing whitespace, WSL notes).

## Security notes

See [security.md](security.md). Short version: the scripts make no network calls,
need no elevated privileges, and work only in a self-deleting temp directory — but
remember that **hooks run code**, so always read a hook before installing one from
an untrusted source.

## Extension exercises

1. Make the pipeline observable: copy `examples/pipeline.sh` to your own file and
   have every run append a timestamped line to `pipeline.log` recording which
   stage it reached and whether it succeeded.
2. Add a check to your hook that rejects a commit if a staged `.sh` file fails a
   `bash -n` syntax check, then prove it blocks a broken file and allows a fixed one.
3. Sketch a CI version: write (do not run) a short list of the same stages your
   pipeline runs, and note which checks you would keep local for speed and which
   you would move to CI as the authoritative gate.

## Navigation

- **Previous day:** Day 40 — Observability: Logs, Metrics, Traces, and Dashboards (`labs/sections/computing-foundations/day-040-observability-logs-metrics-traces-and-dashboards/`).
- **Next day:** Day 42 — Section Review: Your Computing Foundations Toolkit (`labs/sections/computing-foundations/day-042-section-review-your-computing-foundations-toolkit/`).
