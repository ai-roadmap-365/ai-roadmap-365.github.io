# Day 035 lab — A Real Git Workflow

Day number: 35 of 365. This lab runs a complete team git workflow end to end —
branch, atomic commits, reviewed merge, and a semantic-versioned release tag —
entirely on your own machine, with no network and no account.

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Git Workflows for Real Projects
- **Day number:** 35 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-035-git-workflows-for-real-projects
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-035-git-workflows-for-real-projects` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 35's lesson explains how a team puts git to work: branching strategies,
commit hygiene, release tags, and clean history. This lab makes it real. You
simulate **GitHub Flow** against a **local bare "origin"** — create a
short-lived feature branch, make atomic commits with Conventional Commit
messages, merge back with `--no-ff` (as if merging a pull request), and tag a
`v1.0.0` release with an annotated tag — then read the history you built. It is
exactly the workflow the Versioned Notes Repository project asks for.

## Learning objectives

- Run a full GitHub Flow cycle: branch, commit, merge, tag.
- Write atomic commits with `feat:` and `fix:` Conventional Commit messages.
- Merge a feature branch with `--no-ff` so the merge is recorded like a pull request.
- Create an annotated release tag (`git tag -a`) and choose a semantic version.
- See a `.gitignore` keep a file out of git, and contrast atomic with sloppy commits.

## Prerequisites

- The Day 35 lesson (read it first — it explains every concept this lab exercises).
- Days 29-34: commits, branching and merging, remotes, pull requests, and undoing changes.
- `git` (2.23+) and a terminal. No programming experience required; every command is given.

## Supported operating systems

- **macOS** — fully supported (tested on macOS, Apple Silicon).
- **Linux** — fully supported (any distribution with git and bash).
- **Windows** — run inside WSL and follow the Linux path; native PowerShell is
  not supported for these bash scripts.

## Hardware requirements

Any computer that can run git. The lab creates a few tiny text files in a
temporary directory and needs no special CPU, RAM, disk, or GPU.

## Required software

- `git` 2.23 or newer (for `git switch`; older git works with the
  `git checkout` equivalents noted in `troubleshooting.md`).
- `bash` 3.2 or newer, plus standard utilities (`mktemp`, `printf`, `grep`,
  `awk`, `sed`) — all preinstalled.

## Free and open-source options

Everything here is free and open source: git and every command used ship with
your OS or are open-source tools. No account, key, or purchase is needed, and
the lab never touches the network — the "remote" is a local bare repository.

## Installation

None beyond git. Clone the repository (or copy this directory) and change into it:

```bash
cd labs/sections/computing-foundations/day-035-git-workflows-for-real-projects
```

## File structure

```text
day-035-git-workflows-for-real-projects/
├── README.md                        ← you are here
├── metadata.yml                     ← machine-readable lab metadata
├── starter/
│   ├── workflow_demo.sh             ← YOUR working file (5 exercises)
│   └── workflow-worksheet.md        ← record your branch/merge/tag/semver steps
├── examples/
│   └── workflow_demo.sh             ← completed reference implementation
├── tests/
│   └── run_tests.sh                 ← automated behavioral checks
├── expected-output/
│   ├── sample-run.txt               ← real captured run of the reference
│   ├── tests-run.txt                ← real captured test run
│   └── FIELDS.md                    ← what a correct run must contain
├── requirements/
│   └── README.md                    ← dependency statement (git + shell)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished workflow execute first
bash examples/workflow_demo.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/workflow_demo.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/workflow_demo.sh` — creates a throwaway working repo and a
  local bare `origin` in a `mktemp` directory, sets a repository-local git
  identity, commits a `.gitignore` (`chore:`), branches off `main`
  (`feat/notes-search`), makes a `feat:` and a `fix:` atomic commit, merges
  back with `git merge --no-ff`, tags `v1.0.0` with `git tag -a`, pushes to the
  local origin, illustrates atomic-vs-sloppy commits, then prints `git tag` and
  `git log --oneline --decorate --graph`. The temp directory is deleted on exit.
- `bash starter/workflow_demo.sh` — the same skeleton with five numbered
  exercises. Each `__FILL_ME_IN__` line names the exact git command to write in
  its place. Edit the file, then run it.
- `bash tests/run_tests.sh` — runs the workflow and checks the resulting
  history: a feature branch merged into `main`, an annotated `v1.0.0` tag, and
  `feat:`/`fix:` Conventional Commit messages; plus that the starter names all
  five exercises and that no lab script contains a network URL.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run. The history section looks like this (hashes and temp paths will
differ):

```text
=== Tags ===
v1.0.0
=== History (main) ===
*   87ff7e2 (HEAD -> main, tag: v1.0.0, origin/main) Merge branch 'feat/notes-search'
|\
| * 7f8bc99 (feat/notes-search) fix: handle empty query without crashing
| * 3c188b4 feat: add case-insensitive note search
|/
* 538d3a1 chore: initialize notes repository with .gitignore
=== Workflow demo complete ===
```

The merge commit sits on top with `v1.0.0` pinned to it; the `feat:` and `fix:`
commits are on the merged branch below; the initial `chore:` commit is at the
base. See [`expected-output/FIELDS.md`](expected-output/FIELDS.md) for the full
list of what every correct run must contain.

## Validation steps

1. Run `bash starter/workflow_demo.sh` after completing the exercises — it must
   exit without errors and print the Tags and History sections.
2. Confirm the History shows a **merge commit** at the top (proof of `--no-ff`).
3. Confirm the Tags section lists **`v1.0.0`** and the log shows `tag: v1.0.0`.
4. Confirm you see one **`feat:`** and one **`fix:`** commit message.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `8 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It needs no network.

## Cleanup

Nothing to clean up: both scripts do all their work inside a `mktemp`
directory and delete it on exit. To reset your edited starter, restore it from
git: `git checkout -- starter/workflow_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (git version and
`git switch`, identity errors, fast-forward merges, annotated vs lightweight
tags, deleting a tag, and WSL notes).

## Security notes

See [security.md](security.md). Short version: everything runs in a temporary
directory that is deleted on exit, there are no network calls or credentials,
your global git identity is never modified, and the fake `.env` is a teaching
prop that is never committed.

## Extension exercises

1. Add a second feature branch, merge it with `--no-ff`, and cut a `v1.1.0`
   tag — then note why the bump is MINOR, not PATCH or MAJOR.
2. Generate a changelog by hand: `git log --oneline` and group commits under
   **Features** (`feat:`) and **Fixes** (`fix:`), as changelog tools do.
3. Inspect the two tag kinds: create a lightweight tag (`git tag tmp`) and
   compare `git show tmp` with `git show v1.0.0` to see what the annotation adds.

## Navigation

- **Previous day:** Day 34 — Undoing Things: Reset, Revert, and Reflog
  (`labs/sections/computing-foundations/day-034-undoing-things-reset-revert-and-reflog/`).
- **Next day:** Day 36 — Choosing and Configuring a Code Editor
  (`labs/sections/computing-foundations/day-036-choosing-and-configuring-a-code-editor/`, to be written).
