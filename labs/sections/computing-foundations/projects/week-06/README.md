# Week 06 project — Automated Quality Pipeline (Course 1 capstone)

This is the final project of **Course 1: Computing Foundations**. It ties
together the whole section — the shell, git, scripting, storage,
observability, and automation — into one small but real quality pipeline
you could drop into any project.

## What you are building

A git repository with an **automated quality pipeline**: on every commit, a
pre-commit hook runs formatting and lint checks and a smoke test; the run is
logged in a structured, inspectable way; and a pipeline script runs the
stages in order and fails fast. It is a miniature of how professional (and
AI/ML) projects gate every change.

## What it must include (drawing on all of Course 1)

- **A git repo** with a clean history and a `.gitignore` (Weeks 5, 2).
- **A pre-commit hook** (Day 41) that runs, in order and failing fast:
  - a **format check** (trailing whitespace / final newline — Day 36's
    EditorConfig rules) and
  - a **lint / syntax check** (`bash -n`, or ShellCheck if installed —
    Day 37), and
  - a **smoke test** (a tiny test script that must pass — Day 12).
- **Structured logging** of each pipeline run to a log file (Day 40), so you
  can see what ran and whether it passed.
- **A `pipeline.sh`** that runs the same stages manually (lint → test →
  build) and fails fast (Day 41), so the checks work in CI too.
- **A short README** documenting how to run it and what each stage does.

## Steps

1. `git init` a repo; add `.gitignore` and a trivial script + its test.
2. Write `pipeline.sh` with lint → test → build stages that fail fast and
   log each stage's result.
3. Install a `.git/hooks/pre-commit` that runs `pipeline.sh` (or its checks)
   and blocks the commit on failure.
4. Prove it works: a commit with a lint/format/test problem is **blocked**;
   a clean commit **passes** and is logged.
5. Validate against the checklist.

## Expected output

- Committing a file with trailing whitespace or a failing test is rejected
  by the hook with a clear message; the commit does not happen.
- A clean commit passes all stages and appends a structured log line
  recording the run.
- Running `pipeline.sh` manually reproduces the same checks and fails fast on
  the first failing stage.

## Validation

- [ ] `.gitignore` present; no secrets or junk committed.
- [ ] A working `pre-commit` hook that blocks a bad commit and allows a clean
      one.
- [ ] The pipeline runs format → lint → test in order and fails fast.
- [ ] Each run is logged in a structured, greppable form (Day 40).
- [ ] A README documents the stages and how to run them.
- [ ] You can explain which Section-1 day each piece came from.

## Troubleshooting

- Hook not running? Make it executable: `chmod +x .git/hooks/pre-commit`.
- Need to bypass in an emergency? `git commit --no-verify` — but understand
  why you normally shouldn't (Day 41).
- ShellCheck not installed? The lint stage should degrade to `bash -n` and
  say so (Day 37) — don't fail just because an optional tool is absent.
- Revisit the toolkit-check from Day 42 if any required tool is missing.
