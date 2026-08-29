# Day 030 lab — Init, Stage, Commit

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Git Fundamentals: Repositories, Staging, and Commits
- **Day number:** 30 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-030-git-fundamentals-repositories-staging-and-commits
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-030-git-fundamentals-repositories-staging-and-commits` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 30's lesson builds the mental model of Git's three areas — working
directory, staging area, and repository — and what a commit really is. This
lab makes that model physical: you drive a **throwaway** Git repository by
hand and watch a single file move from untracked, to staged, to committed, then
see a `.gitignore` keep a secret out of history. Nothing here touches your real
projects or your global Git configuration, and it runs entirely offline.

## Learning objectives

- Initialise a repository with `git init` and recognise the `.git` directory.
- Read `git status --short` codes (`??`, `A `, ` M`) and name which of the
  three areas holds the current content at each step.
- Move a file through the flow with `git add` (stage) and `git commit`
  (record), and confirm two commits accumulate in the history.
- Use `git diff` to see an unstaged change, and `git log --oneline` to read
  history newest-first.
- Use `.gitignore` to keep a file untracked, and prove it with
  `git check-ignore`.

## Prerequisites

- The Day 30 lesson (read it first — it explains every concept this lab
  exercises).
- The Day 29 idea of why version control exists.
- A terminal and Git installed (`git --version` prints a 2.x version).
- No prior Git experience: every command is given and explained.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, Git 2.50.1).
- **Linux** — fully supported (any distribution with Git and a POSIX shell).
- **Windows** — use WSL or Git Bash and follow the same commands.

## Hardware requirements

Any computer that can run Git. The lab creates a tiny temporary repository with
a handful of small text files; it needs no meaningful RAM, disk, or GPU.

## Required software

- `git` (any 2.x release).
- `bash` (3.2+) and standard utilities: `mktemp`, `printf`, `sed`, `grep`,
  `ls`, `rm` — all preinstalled on macOS and Linux.

See [`requirements/README.md`](requirements/README.md) for install commands.

## Free and open-source options

Git is free and open-source (GPLv2), and every utility this lab uses ships
with your OS. No account, API key, purchase, or network connection is needed.

## Installation

None beyond Git itself. From the repository root:

```bash
cd labs/sections/computing-foundations/day-030-git-fundamentals-repositories-staging-and-commits
git --version   # confirm Git is installed
```

## File structure

```text
day-030-git-fundamentals-repositories-staging-and-commits/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── git_basics.sh               ← YOUR working file (5 exercises)
│   └── git-worksheet.md            ← record states, hashes, and what was ignored
├── examples/
│   └── git_basics.sh               ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (12)
├── expected-output/
│   ├── sample-run.txt              ← a real captured run (macOS, Git 2.50.1)
│   └── FIELDS.md                   ← which lines are stable vs. which vary
├── requirements/
│   └── README.md                   ← dependency statement (just Git)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/git_basics.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/git_basics.sh

# 3. Check everything
bash tests/run_tests.sh
```

Then fill in [`starter/git-worksheet.md`](starter/git-worksheet.md) from what
you saw.

## What the commands do

- `bash examples/git_basics.sh` — the reference walkthrough. It creates a
  temporary repo under this directory, gives it a local identity, then runs
  the full flow: `git init`, `git status` on an untracked file, `git add`,
  `git commit`, an edit, `git diff` on the unstaged change, `git add` +
  `git commit`, a `.gitignore` that keeps `secret.key` untracked, and
  `git log --oneline`. It deletes the temp repo on exit.
- `bash starter/git_basics.sh` — the same skeleton with five `FILL_ME` lines.
  Each exercise comment names the exact command to type in its place. Edit the
  file in any text editor, then run it.
- `bash tests/run_tests.sh` — builds its own throwaway repo and asserts real
  Git behaviour: init works, a new file is untracked, `git add` stages it,
  commits accumulate to 2+, an edit shows as modified-but-unstaged,
  `.gitignore` excludes a file, `HEAD` resolves, and no remote exists (proving
  it is fully local). It also runs the reference script and checks it leaves no
  directory behind.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run. The step banners, status codes, diff hunk, and the three-line
`git log --oneline` are identical every run; **commit hashes differ every run**
because a hash is computed from the snapshot content plus the commit time and
author. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) says exactly
which lines are stable and which vary.

A trimmed excerpt:

```text
----- 2. git status — a brand-new file is UNTRACKED -----
?? notes.txt

----- 3. git add — move notes.txt into the STAGING AREA -----
A  notes.txt

----- 8. git log --oneline — read the history (newest first) -----
945beab Add .gitignore to exclude secret.key
712412c Append a second line to notes.txt
fa3f66b Add notes.txt with initial notes
```

## Validation steps

1. Run `bash examples/git_basics.sh` — it must exit without errors and print
   three commits under `git log --oneline`.
2. Confirm `secret.key` never appears in any `git status` output.
3. Complete `starter/git_basics.sh` (replace all five `FILL_ME` lines) and run
   it — it must print `git log --oneline` with three commits.
4. Run the tests (next section) — all checks must pass.
5. Confirm no `.gitdemo.*` or `.gittest.*` directory is left behind.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `12 checks, 0 failure(s).` The command exits 0 on
success and non-zero on any failure, so it can run in CI. It uses no network.

## Cleanup

Nothing to clean up in normal use: both scripts delete their temporary
repository on exit. If a run was interrupted (e.g. Ctrl-C), remove any leftover
with:

```bash
rm -rf .gitdemo.* .gittest.*
```

To reset your edits to the starter, restore it from version control:
`git checkout -- starter/git_basics.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — covers "identity not set",
`nothing to commit, working tree clean`, a `.gitignore` that does not seem to
work, and Windows notes.

## Security notes

See [security.md](security.md). Short version: everything runs in a throwaway
temp directory with a local identity, makes no network calls, needs no
privileges, and demonstrates keeping secrets out of a repository with
`.gitignore` — a habit the course reinforces.

## Extension exercises

1. Run `git cat-file -p HEAD` in a temp repo to print the raw commit object and
   find its `tree`, `parent`, `author`, and message fields — the anatomy the
   lesson describes.
2. Stage part of a change with `git add -p` (patch mode) and commit only some
   hunks, leaving the rest in the working directory. Confirm with `git status`.
3. Add a second ignore pattern (e.g. `*.log`) to `.gitignore`, create a
   matching file, and verify with `git check-ignore -v` which rule matched.

## Navigation

- **Previous day:** Day 29 — Why Version Control Exists
  (`labs/sections/computing-foundations/day-029-why-version-control-exists/`).
- **Next day:** Day 31 — Branching and Merging
  (`labs/sections/computing-foundations/day-031-branching-and-merging/`).
