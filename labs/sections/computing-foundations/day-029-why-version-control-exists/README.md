# Day 029 lab — Your First Repository's History

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Why Version Control Exists
- **Day number:** 29 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-029-why-version-control-exists
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-029-why-version-control-exists` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 29's lesson explains *why* version control exists. This lab makes it
concrete without asking you to learn any commands yet: a short script builds a
real, throwaway git repository, makes three commits to one file, and then
shows you the history four ways — the one-line log, a diff between two
versions, the full detail of one commit, and a restore of an earlier version
(the "time machine"). You watch history get built and then travel through it,
all locally, with nothing left behind afterward.

## Learning objectives

- See a repository's history as a chain of three commits you can list at a glance.
- Read a diff and identify exactly which line one commit added.
- Read a commit's author, timestamp, and message with `git show`.
- Restore an earlier version of a file and understand why nothing is lost.
- Complete four small exercises that name the exact git commands, and record what you learned in a worksheet.

## Prerequisites

- The Day 29 lesson (read it first — it explains every idea this lab shows).
- A terminal: Terminal.app (macOS), any terminal (Linux), or Git Bash / WSL (Windows).
- `git` installed (or installable — see [Installation](#installation)); no prior version control experience required.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, git 2.50.1).
- **Linux** — fully supported (any distribution with `git` and a POSIX shell).
- **Windows** — use Git Bash (bundled with Git for Windows), or run the scripts unmodified inside WSL.

## Hardware requirements

Any computer that runs git. The lab creates a tiny temporary repository and a
few small text files; it needs no meaningful RAM, disk, or GPU.

## Required software

- `bash` (3.2 or newer — preinstalled on macOS and Linux).
- `git` (any 2.x release; `git restore` needs 2.23+, and the scripts fall back to `git checkout` on older git).
- Standard utilities only: `mktemp`, `printf`, `cat`, `grep`, `sed`, `awk` — all part of the base system.

## Free and open-source options

Everything here is free and open source: git itself, bash, and every utility
used. No account, API key, network connection, or purchase is required — git
is the free, open-source standard this whole week teaches.

## Installation

Confirm git is present:

```bash
git --version
```

If that prints a version, you are ready. If not, install git (it is free
everywhere) — full per-platform instructions are in
[`requirements/README.md`](requirements/README.md). Then change into this
directory:

```bash
cd labs/sections/computing-foundations/day-029-why-version-control-exists
```

## File structure

```text
day-029-why-version-control-exists/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── history_demo.sh             ← YOUR working file (4 exercises)
│   └── vcs-worksheet.md            ← worksheet for the practice assignment
├── examples/
│   └── history_demo.sh             ← completed reference demo
├── tests/
│   └── run_tests.sh                ← automated checks
├── expected-output/
│   ├── sample-run.txt              ← a real captured run (macOS)
│   └── FIELDS.md                   ← what is stable vs. what varies per run
├── requirements/
│   └── README.md                   ← how to install git (the only dependency)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished demo first
bash examples/history_demo.sh

# 2. Your task: complete the four exercises in the starter, then run it
bash starter/history_demo.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/history_demo.sh` — creates a throwaway git repository in a
  temporary directory, sets a *local* git identity (so it works even if you
  have never configured git), makes three commits to `notes.txt`, then runs
  `git log --oneline`, a `git diff` between commits 1 and 2, a `git show` of
  commit 2, and a restore of `notes.txt` to commit 1 — deleting the temporary
  directory on exit.
- `bash starter/history_demo.sh` — the same script with the four inspection
  steps left as numbered exercises; each comment names the exact git command
  to fill in (`git log --oneline`, `git diff`, `git show`, `git restore`).
- `bash tests/run_tests.sh` — runs the reference demo and checks real
  behavior: three commits made, three commits in the log, a diff showing an
  added line, `git show` revealing the author, the restore returning commit
  1's content, and the temporary directory gone afterward — then confirms the
  starter names the four required commands.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run. The shape is fixed but the commit ids and the temporary
path differ every run:

```text
=== Version control history demo ===
Creating a throwaway repository in a temporary directory...
(temporary directory: /var/folders/.../day029-vcs-demo.XXXXXX)
Made commit 1: Start notes with a first point
Made commit 2: Expand the notes with a second point
Made commit 3: Add a closing line to the notes

--- git log --oneline (newest first) ---
ee169af Add a closing line to the notes
5da934c Expand the notes with a second point
64258c3 Start notes with a first point

--- git diff between commit 1 and commit 2 (notes.txt) ---
+Point two: every commit records who, when, and why.

--- git show of commit 2 ---
Author: Course Learner <learner@example.com>
    Expand the notes with a second point

--- Time machine: restoring notes.txt to commit 1 ---
Restored. notes.txt now reads:
Point one: version control keeps history.

Cleaning up the temporary repository...
Done. Nothing left behind.
```

Your commit ids will differ — that is expected, because a commit's id is a
hash of its content, author, and time. [`expected-output/FIELDS.md`](expected-output/FIELDS.md)
lists exactly what stays stable and what varies.

## Validation steps

1. Run `bash examples/history_demo.sh` — it must exit without errors and print three "Made commit" lines.
2. Confirm `git log --oneline` shows exactly three commits, newest first.
3. Confirm the diff shows the single added line `+Point two: ...`.
4. Confirm the restore step brings back `Point one: version control keeps history.`.
5. Confirm the final two lines report cleanup, and that the temporary directory named near the top no longer exists.
6. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `12 checks, 0 failure(s).` (8 behavior checks against
the reference demo — including that its temporary directory is gone
afterward — and 4 checks that the starter names the four required git
commands.) The command exits 0 on success and non-zero on any failure, so it
can run in CI. It uses no network.

## Cleanup

Nothing to clean up: each script deletes its own temporary directory on exit,
even if interrupted. To reset your edits to the starter, restore it from git:
`git checkout -- starter/history_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list — git not
installed, the "author identity unknown" message (the scripts set a local one),
`git restore` on older git, a lingering temporary directory after Ctrl-C, and
Windows notes.

## Security notes

See [security.md](security.md). Short version: the scripts operate only inside
a temporary directory they create and delete, set **no global git config**,
make no network calls, and need no elevated privileges.

## Extension exercises

1. Copy `examples/history_demo.sh`, remove the cleanup `trap` line, run it, then `cd` into the temporary directory and explore: `git log --stat` (which files changed and by how much) and `git cat-file -p HEAD` (the raw commit object — tree, parent, author, message). Delete the folder yourself when done.
2. Add a fourth commit that *removes* a line, then diff it against the third commit and read how deletions appear (with a leading `-`).
3. Create a second branch in your throwaway repo (`git switch -c experiment`), make a commit on it, and use `git log --oneline --graph --all` to see the branch structure you read about in the lesson.

## Navigation

- **Previous day:** Day 28 — Consuming a Public API from the Command Line (`labs/sections/computing-foundations/day-028-consuming-a-public-api-from-the/`).
- **Next day:** Day 30 — Git Fundamentals: Repositories, Staging, and Commits (`labs/sections/computing-foundations/day-030-git-fundamentals-repositories-staging-and-commits/`, to be written).
