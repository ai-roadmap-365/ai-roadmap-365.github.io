# Day 032 lab — Remotes Without a Network

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Remotes and GitHub
- **Day number:** 32 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-032-remotes-and-github
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-032-remotes-and-github` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 32's lesson explains how Git connects one copy of a repository to another
through a **remote**, and what platforms like GitHub add on top. This lab
makes it concrete and truthful **without any network or account**: you use a
local **bare repository** as the remote and run the full clone / push / fetch
/ pull cycle end to end. Every command is exactly the one you would run
against a real hosting platform — only the address is a folder path.

## Learning objectives

- Register a remote with `git remote add` and inspect it with `git remote -v`.
- Push commits to a remote and set an upstream with `git push -u origin main`.
- Clone a remote into a second working copy and confirm it received the history.
- Move a change between two clones using `push`, `fetch`, and `pull`.
- Read tracking information with `git branch -vv` and explain what `origin/main` is.

## Prerequisites

- Days 29–31: version control concepts, Git repositories, commits, and merging.
- Git installed (`git --version`) and a terminal.
- **No** GitHub account, network, or authentication is required.

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon).
- **Linux** — fully supported (any distribution with Git and bash).
- **Windows** — use WSL (Windows Subsystem for Linux) and follow the Linux
  path; native Git Bash also works.

## Hardware requirements

Any computer that can run Git. The lab creates a few tiny text files in a
temporary folder and needs no special CPU, RAM, GPU, or disk.

## Required software

- `git` (2.28+ recommended for `git init -b main`; older-Git fallback is in
  `troubleshooting.md`).
- `bash` (3.2+), and standard utilities `mktemp`, `ls`, `sed`, `grep` — all
  preinstalled.

## Free and open-source options

Everything here is free and open source: Git itself, bash, and every utility
used. No account, API key, or purchase is needed. When you later try a real
remote, the free tiers of GitHub, GitLab, Bitbucket, and self-hosted Gitea
are all more than enough (see the lesson's comparison table).

## Installation

None. Clone the repository (or copy this directory) and change into it:

```bash
cd labs/sections/computing-foundations/day-032-remotes-and-github
```

## File structure

```text
day-032-remotes-and-github/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── remote_demo.sh              ← YOUR working file (5 exercises)
│   └── remotes-worksheet.md        ← worksheet for the practice assignment
├── examples/
│   └── remote_demo.sh              ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (12 checks, no network)
├── expected-output/
│   ├── sample-run.txt              ← real captured run of the reference script
│   ├── tests-run.txt               ← real captured test run
│   └── FIELDS.md                   ← what a correct run must show, per platform
├── requirements/
│   └── README.md                   ← dependency statement (git only)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the finished result first
bash examples/remote_demo.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/remote_demo.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/remote_demo.sh` — runs the reference cycle: creates a bare
  repo as `origin` in a temp folder, registers it in a working repo, pushes
  with `-u`, clones the remote a second time, commits and pushes from the
  clone, then pulls the change back into the first copy. It prints
  `git remote -v` and `git branch -vv` so you can see the remote and the
  tracking branch. The temp workspace is deleted automatically on exit.
- `bash starter/remote_demo.sh` — the same flow with five git commands
  blanked out as `REPLACE_ME`. Each exercise comment names the exact command;
  edit the file and replace each `REPLACE_ME` line, then re-run.
- `bash tests/run_tests.sh` — independently performs a push/clone/pull cycle
  and asserts real behaviour (push succeeds, the clone receives the file, a
  change propagates via pull, the upstream is set, the remote is a local
  path), then runs the reference script and checks its output. Exits 0 on
  success.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a
real captured run. Key lines to look for: `* [new branch]      main -> main`
(the push), `branch 'main' set up to track 'origin/main'.` (the upstream),
`Fast-forward` (the pull), and `shared.txt present in repo-a: yes` (the
change arrived). Your temporary paths and commit hashes will differ — that is
expected. [`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists what
a correct run must show on every platform.

## Validation steps

1. Run `bash examples/remote_demo.sh` — it must finish with
   `=== Done: a change travelled repo-b -> origin -> repo-a, with no network. ===`.
2. Complete the five exercises in `starter/remote_demo.sh` until running it
   prints `All five exercises look complete.` and no line reports an
   unfinished exercise.
3. Confirm `git remote -v` in the demo points at a **local folder**, never a
   web URL.
4. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `12 checks, 0 failure(s).` The command exits 0 on
success and non-zero on any failure, so it can run in CI. It needs no
network.

## Cleanup

Nothing to clean up: both scripts do all their work inside a `mktemp`
temporary directory that is removed automatically on exit. To reset your
starter edits, restore the file from git:
`git checkout -- starter/remote_demo.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the bare-repository trick,
the older-Git fallback, the rejected-push fix, and pointers for authenticating
to a real GitHub/GitLab/Bitbucket remote with a token or SSH key.

## Security notes

See [security.md](security.md). Short version: the scripts touch only a temp
directory, make no network calls, and need no privileges — and for real
remotes you should authenticate with an SSH key or a token, never a password
in the URL, and never commit secrets.

## Extension exercises

1. Add a **second** remote (`git remote add backup <another-bare-path>`),
   push `main` to both, then make a commit and push it to only one. Use
   `git remote -v` and `git branch -vv` to see that a repo can track several
   remotes independently.
2. Deliberately trigger a rejected push: commit directly in the clone and in
   the first repo without syncing, push one, then try to push the other.
   Read the rejection message, then resolve it with `git pull` and push again.
3. Inspect the bare repository directly with
   `git --git-dir=<origin.git> log --oneline` to confirm it holds the shared
   history even though it has no working files.

## Navigation

- **Previous day:** Day 31 — Branching and Merging
  (`labs/sections/computing-foundations/day-031-branching-and-merging/`).
- **Next day:** Day 33 — Pull Requests and Code Review
  (`labs/sections/computing-foundations/day-033-pull-requests-and-code-review/`, to be written).
