# Day 033 lab — Simulate a Pull Request Locally

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Pull Requests and Code Review
- **Day number:** 33 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-033-pull-requests-and-code-review
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-033-pull-requests-and-code-review` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 33's lesson explains the pull-request-and-review workflow: propose a change
on a branch, open a PR, review and iterate, then merge. This lab makes it
concrete **without needing a GitHub account or a network connection**. Because a
pull request is just review and merge gates wrapped around Git branches and
merges, you rehearse the whole loop locally: make a change on a `feature`
branch, produce the exact diff and commit log a pull request would show,
simulate a round of review with a follow-up commit, then merge two different
ways to see how the choice of merge strategy shapes history.

## Learning objectives

- Create a feature branch and make a single, focused commit — the substance of a
  pull request.
- Produce a pull request's core artifacts locally: `git diff main..feature` and
  `git log main..feature`.
- Simulate the review-and-iterate loop by adding an "addressed feedback" commit.
- Merge with `--no-ff` to create a merge commit, exactly as a pull-request merge
  does, and read the result in `git log --graph`.
- Contrast the squash strategy (`git merge --squash`) and see it collapse a
  branch into a single commit on `main`.

## Prerequisites

- The Day 33 lesson (read it first — it explains every concept this lab makes
  concrete).
- Days 30–32: comfort creating branches, committing, and merging with Git.
- A terminal and Git installed (`git --version` should print 2.0 or newer; 2.23+
  preferred).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with bash and system Git).
- **Linux** — fully supported (any distribution with `git`, `bash`, `mktemp`,
  `sed`).
- **Windows** — use Git Bash or WSL, where the scripts run unmodified. Plain
  PowerShell is not supported for this lab.

## Hardware requirements

Any computer that can run Git. The lab creates a tiny temporary repository and
writes nothing of size.

## Required software

- `git` (2.0 or newer; 2.23+ enables `git switch`, but the scripts fall back to
  `git checkout` automatically).
- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard utilities `mktemp`, `sed`, `printf` (all preinstalled).

## Free and open-source options

Everything here is free and open source: Git itself and every command used ship
with your OS or are freely installable. No account, API key, network, or
purchase is needed. A *real* pull request additionally needs a free account on a
hosting platform and network access; this lab covers that side conceptually so
you can practice the mechanics offline.

## Installation

None beyond Git. Clone the repository (or copy this directory) and change into
it:

```bash
cd labs/sections/computing-foundations/day-033-pull-requests-and-code-review
```

## File structure

```text
day-033-pull-requests-and-code-review/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── pr_flow.sh                  ← YOUR working file (5 exercises)
│   └── pr-worksheet.md             ← worksheet for the practice assignment
├── examples/
│   └── pr_flow.sh                  ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (11 checks)
├── expected-output/
│   ├── sample-run.txt              ← a real captured run
│   └── FIELDS.md                   ← the landmarks every run must show
├── requirements/
│   └── README.md                   ← dependency statement (just Git)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished flow first
bash examples/pr_flow.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/pr_flow.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/pr_flow.sh` — runs the reference flow in a throwaway repo:
  creates a `feature` branch, commits a focused change, prints
  `git diff main..feature` and `git log main..feature` (the pull request), adds
  an "addressed feedback" commit, merges with `git merge --no-ff` to create a
  merge commit, and then contrasts a `git merge --squash` on a second branch.
  The repo is deleted on exit.
- `bash starter/pr_flow.sh` — the same flow with five numbered exercises for you
  to complete. Each `: "FILL-IN ..."` line names the exact command to substitute
  (`git switch -c feature`, `git add`/`git commit`, `git diff`/`git log`,
  `git merge --no-ff`). Edit the file, replace every `FILL-IN` line, then run it.
- `bash tests/run_tests.sh` — checks that the starter is valid bash and still
  has its five exercises, then runs the reference flow in an inspectable repo and
  verifies the real Git state: the `feature` branch exists with the focused
  change and the review follow-up commit, a two-parent merge commit was created
  by `--no-ff`, and the squash landed a second branch as a single commit on
  `main`.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run. Commit hashes and the temp-directory path differ on every run;
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists the landmarks that
must appear regardless. The key moments:

```text
== Step 5: merge the PR with a merge commit (--no-ff) ==
History after the merge (note the two-parent merge commit):
*   8140fdc Merge branch 'feature'
|\
| * 123e011 Address review: clarify wording
| * ec70f7e Add greeting line to notes
|/
* 188b3b9 Initial notes
```

The two-parent merge commit is exactly what a pull-request merge produces; the
squash step later shows the contrasting single-commit history.

## Validation steps

1. Run `bash examples/pr_flow.sh` — it must exit without errors and print both
   the merge-commit graph (Step 5) and the squashed commit (Step 6).
2. Complete `starter/pr_flow.sh`, replacing every `FILL-IN` line, and run it —
   it must reach the final `== Done ... ==` line.
3. Confirm the merge graph shows a two-parent merge commit and the squash shows
   a single commit on `main`.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `11 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It uses no network.

## Cleanup

Nothing to clean up: every script works inside a temporary directory that is
deleted on exit, and nothing is written into this repository or your home
directory. To reset your edits to the starter, restore it from git:
`git checkout -- starter/pr_flow.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list (Git not
installed, missing identity, `git switch` on older Git, fast-forward vs merge
commit, `sed -i` portability, graph glyphs).

## Security notes

See [security.md](security.md). Short version: the scripts run no network calls,
need no elevated privileges, work only in a temporary directory, and set the
commit identity **locally** so your global Git config is never touched.

## Extension exercises

1. Before merging, run `git log main..feature --stat` to see the per-file line
   counts a reviewer scans to judge how big a change is.
2. Deliberately create a merge conflict: change the same line on `main` that
   your `feature` branch changed, commit it, then merge — resolve the conflict,
   `git add` the file, and complete the merge. This mirrors a hosting platform
   reporting "this branch has conflicts."
3. Try the `rebase and merge` strategy: `git switch feature`, then
   `git rebase main`, then a fast-forward merge into `main`. Compare the
   resulting linear history with the merge-commit and squash graphs.

## Navigation

- **Previous day:** Day 32 — Remotes and GitHub
  (`labs/sections/computing-foundations/day-032-remotes-and-github/`).
- **Next day:** Day 34 — Undoing Things: Reset, Revert, and Reflog
  (`labs/sections/computing-foundations/day-034-undoing-things-reset-revert-and-reflog/`, to be written).
