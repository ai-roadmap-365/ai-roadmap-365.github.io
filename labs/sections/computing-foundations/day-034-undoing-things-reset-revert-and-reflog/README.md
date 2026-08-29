# Day 034 lab — Undo and Recover

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Undoing Things: Reset, Revert, and Reflog
- **Day number:** 34 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-034-undoing-things-reset-revert-and-reflog
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-034-undoing-things-reset-revert-and-reflog` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 34's lesson explains how Git lets you fix mistakes safely and recover
work that looks lost. This lab makes it real: on a **throwaway repository**
you create just for practice, you amend a commit, un-stage and discard
changes, rewind with `git reset`, undo with `git revert`, and then stage a
deliberate "disaster" — dropping two commits with `git reset --hard` — and
**recover them from the reflog**, proving with your own hands that committed
work is almost impossible to truly lose.

## Learning objectives

- Fix the last commit's message with `git commit --amend` and see the hash change.
- Un-stage a file with `git restore --staged` and discard an edit with `git restore`.
- Observe what `git reset --soft` and `git reset --hard` each do to staged and edited files.
- Create an inverse commit with `git revert`.
- Recover commits dropped by `git reset --hard` using `git reflog` and `git reset --hard <hash>`.

## Prerequisites

- The Day 34 lesson (read it first — it explains every command this lab runs).
- Days 29–32: Git basics (`init`, `add`, `commit`, branches, remotes).
- A terminal and a working Git install (`git --version` should print 2.23+).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, git 2.50.1).
- **Linux** — fully supported (any distribution with Git and `bash`).
- **Windows** — run inside WSL or Git Bash; the commands are identical there.

## Hardware requirements

Any computer that can run Git. The lab creates a tiny repository in a
temporary directory and needs no meaningful disk, RAM, or GPU.

## Required software

- `git` (2.23 or newer, so `git restore` is available).
- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- Standard utilities `mktemp`, `rm`, `tail` — all preinstalled.

## Free and open-source options

Everything here is free and open source: Git itself, bash, and every command
used. No account, API key, network access, or purchase is required.

## Installation

None. Clone the repository (or copy this directory) and you are ready:

```bash
cd labs/sections/computing-foundations/day-034-undoing-things-reset-revert-and-reflog
```

## File structure

```text
day-034-undoing-things-reset-revert-and-reflog/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── undo_recover.sh             ← YOUR working file (5 exercises)
│   └── undo-worksheet.md           ← worksheet for the practice assignment
├── examples/
│   └── undo_recover.sh             ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks
├── expected-output/
│   ├── sample-run.txt              ← real captured run (macOS, git 2.50.1)
│   └── FIELDS.md                   ← what every correct run must show
├── requirements/
│   └── README.md                   ← dependency statement (Git + a shell)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first (safe: it uses a throwaway temp repo)
bash examples/undo_recover.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/undo_recover.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/undo_recover.sh` — creates a temporary Git repository, builds
  a three-commit history, then demonstrates every undo move: `git commit
  --amend`, `git restore --staged`, `git restore`, `git reset --soft`, `git
  revert`, and finally a `git reset --hard HEAD~2` disaster recovered via `git
  reflog`. The temp repo is deleted on exit.
- `bash starter/undo_recover.sh` — the same skeleton with five `# TASK:`
  placeholders. Edit the file and replace each marked line with the exact git
  command named in its comment, then run it; it prints `SUCCESS` when the
  recovery works.
- `bash tests/run_tests.sh` — independently builds its own throwaway repo and
  checks the three core claims: amend changes the last commit, revert creates
  an inverse commit, and a hard reset's dropped commits are recovered via the
  reflog. Exits 0 on success.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run. The final line reads:

```text
SUCCESS: recovered 4 commits — nothing was truly lost.
```

Your commit hashes will differ every run (they are computed from content and
timestamp); only the structure and the successful recovery are fixed.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists exactly what a
correct run must show.

## Validation steps

1. Run `bash examples/undo_recover.sh` — it must end with `SUCCESS: recovered 4 commits`.
2. Complete the five exercises in `starter/undo_recover.sh`; running it must also print `SUCCESS`.
3. Confirm no `REPLACE THIS LINE` or `PLACEHOLDER` marker remains in your starter.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `8 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It uses only a local
throwaway repository — no network, no sudo.

## Cleanup

Nothing to clean up: every script works inside a temporary directory created
with `mktemp` and removed automatically on exit (even on error, via a `trap`).
Your real repositories and global Git config are never touched.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list — reflog
recovery after a hard reset, detached HEAD, the `--hard` warning, old-Git
`restore` equivalents, and identity/`not a git repository` errors.

## Security notes

See [security.md](security.md). Short version: the scripts run no network
calls, need no elevated privileges, and touch only a throwaway temp repo — but
`git reset --hard` discards uncommitted work, so on real projects commit or
stash first.

## Extension exercises

1. Recover a dropped commit **without** the reflog: after a hard reset, run
   `git fsck --lost-found`, find the dangling commit, and restore it with
   `git branch recovered <hash>`.
2. Practise the shared-history rule: make a commit, then undo it two ways — once
   with `git reset` and once with `git revert` — and compare `git log --oneline`
   to see how reset rewrites history while revert grows it.
3. Explore `git reset --soft` for squashing: make three tiny commits, then
   `git reset --soft HEAD~3` and re-commit once, combining them into a single
   clean commit.

## Navigation

- **Previous day:** Day 33 — Pull Requests and Code Review (`labs/sections/computing-foundations/day-033-pull-requests-and-code-review/`, to be written).
- **Next day:** Day 35 — Git Workflows for Real Projects (`labs/sections/computing-foundations/day-035-git-workflows-for-real-projects/`, to be written).
