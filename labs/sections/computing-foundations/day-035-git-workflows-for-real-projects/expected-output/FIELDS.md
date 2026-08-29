# Expected output — Day 035 lab

This directory holds real captured runs from the authoring machine
(macOS, Apple Silicon, git 2.50.x, 2026-07-12). Commit hashes, the temporary
directory name, and the run date will differ on your machine — that is
expected. What must be the same is the *shape* of the result.

## `sample-run.txt`

A full run of `examples/workflow_demo.sh`. A correct run always shows, in order:

1. `=== 1. Initial commit with a .gitignore ===` and a line confirming that
   `.env` is on disk but ignored by git (not tracked).
2. `=== 2. ... ===` with `on branch: feat/notes-search`.
3. `=== 3. ... ===` — two atomic commits are made (no output of their own).
4. `=== 4. ... ===` — the feature branch is merged into `main` with `--no-ff`.
5. `=== 5. ... ===` — an annotated `v1.0.0` tag is created and pushed to the
   local bare `origin`.
6. An atomic-vs-sloppy illustration on a scratch branch.
7. `=== Tags ===` listing `v1.0.0`.
8. `=== History (main) ===` — a `git log --oneline --decorate --graph` showing
   a merge commit at the top carrying `tag: v1.0.0`, the `feat:` and `fix:`
   commits underneath on the merged branch, and the `chore:` initial commit at
   the base.
9. `=== Workflow demo complete ===`.

## `tests-run.txt`

A full run of `bash tests/run_tests.sh`. It ends with `8 checks, 0 failure(s).`
and exits 0. The checks assert that the reference produced a merged feature
branch, an annotated `v1.0.0` tag, and `feat:`/`fix:` Conventional Commit
messages, that the starter names all five exercises, and that no lab script
contains a network URL (the lab is entirely local).

## Platform notes

- **Linux:** identical output. The scripts use only portable git and shell
  features and set a repository-local git identity, so nothing depends on macOS.
- **Windows:** run inside WSL and the output matches the Linux case. Native
  PowerShell is not supported for these bash scripts.
- The scripts create everything under a `mktemp` directory and delete it on
  exit, so no files are left on your machine after a run.
