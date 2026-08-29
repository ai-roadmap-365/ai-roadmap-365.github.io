# Day 031 lab — Branch, Conflict, Merge

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Branching and Merging
- **Day number:** 31 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-031-branching-and-merging
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-031-branching-and-merging` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 31's lesson explains branching and merging in the abstract. This lab makes
it real: in a throwaway repository you create a feature branch, make two
branches disagree about the **same line** of a file, merge them into a genuine
conflict, read the conflict markers git leaves behind, resolve them, and commit
the merge. You also watch a clean **fast-forward** merge for contrast, and
inspect the branching history with `git log --graph`. By the end you have felt
the exact loop you will repeat on every real project.

## Learning objectives

- Create and switch to a branch with `git switch -c`.
- Produce a real three-way merge conflict on purpose and read its markers.
- Resolve a conflict, stage it with `git add`, and complete the merge commit.
- Tell a fast-forward merge from a three-way merge by looking at the history.
- Read a `git log --graph --oneline` diagram and find the merge commit in it.

## Prerequisites

- The Day 31 lesson (read it first — it explains every term this lab uses).
- Day 30's lab habits: `git init`, `git add`, `git commit`, `git log`.
- A terminal with `git` installed (`git --version` should print a version).

## Supported operating systems

- **macOS** — fully supported (tested on macOS with Apple Silicon, git 2.50.1).
- **Linux** — fully supported (any distribution with git ≥ 2.23).
- **Windows** — use Git for Windows' "Git Bash", or run the scripts unmodified
  inside WSL.

## Hardware requirements

Any computer that runs git. The lab writes a few tiny text files into a
temporary directory and deletes them on exit; it needs no meaningful disk, RAM,
or GPU.

## Required software

- `git` ≥ 2.23 (for `git switch`; older git works via the `git checkout`
  substitutions in `troubleshooting.md`).
- `bash` and the standard utilities `mktemp`, `printf`, `sed`, `grep` — all
  preinstalled on macOS and Linux.

## Free and open-source options

Everything here is free and open source: git itself, bash, and every utility
used. No account, API key, network connection, or purchase is required.

## Installation

None beyond git. Move into this directory and you are ready:

```bash
cd labs/sections/computing-foundations/day-031-branching-and-merging
```

If `git --version` fails, see `requirements/README.md` for one-line install
commands per platform.

## File structure

```text
day-031-branching-and-merging/
├── README.md                       ← you are here
├── metadata.yml                    ← machine-readable lab metadata
├── starter/
│   ├── branch_merge.sh             ← YOUR working file (5 exercises)
│   └── branching-worksheet.md      ← record branches, merge type, conflict
├── examples/
│   └── branch_merge.sh             ← completed reference implementation
├── tests/
│   └── run_tests.sh                ← automated checks (build repo, assert git state)
├── expected-output/
│   ├── sample-run.txt              ← a real captured run
│   └── FIELDS.md                   ← what is fixed vs what varies each run
├── requirements/
│   └── README.md                   ← dependency statement (just git)
├── troubleshooting.md
└── security.md
```

## How to run

From this directory:

```bash
# 1. See the whole story run end to end
bash examples/branch_merge.sh

# 2. Your task: complete the five exercises in the starter, then run it
bash starter/branch_merge.sh

# 3. Check your work
bash tests/run_tests.sh
```

Each script builds a fresh temporary repository and deletes it on exit, so you
can run them as many times as you like.

## What the commands do

- `bash examples/branch_merge.sh` — creates a throwaway repo with a local git
  identity, makes a base commit, branches off (`git switch -c`), edits a line
  on the branch, edits the **same line differently** back on `main`, merges the
  branch (`git merge`) into a real conflict, resolves it (`git add` +
  `git commit`), prints the `git log --graph` diamond, and then does a separate
  clean **fast-forward** merge for contrast.
- `bash starter/branch_merge.sh` — the same skeleton with five numbered
  placeholder lines; each exercise comment names the exact git command to type
  in its place. Edit the file, then run it.
- `bash tests/run_tests.sh` — builds its **own** repository and asserts the real
  git outcomes: a branch was created, the merge conflicted, the conflict was
  resolved, the tree ends clean, the tip is a two-parent merge commit, and the
  graph shows the merge. It also runs the example script end to end.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) — a real
captured run. The key moments (commit hashes and the temp path differ every
run — see [`expected-output/FIELDS.md`](expected-output/FIELDS.md)):

```text
--- Step 4: merge feature-blueberries into main (expect a conflict) ---
Auto-merging recipe.txt
CONFLICT (content): Merge conflict in recipe.txt
Automatic merge failed; fix conflicts and then commit the result.
...
<<<<<<< HEAD
milk: 1 cup buttermilk
=======
milk: 2 cups
>>>>>>> feature-blueberries
...
--- Step 6: history graph (the merge commit ties both lines together) ---
*   7c522b2 Merge branch 'feature-blueberries'
|\
| * 84e0a3a feature: use 2 cups of milk
* | fe77868 main: switch to buttermilk
|/
* 493ba6c Add base pancake recipe
```

## Validation steps

1. Run `bash examples/branch_merge.sh` — it must reach the final
   `=== Done. ===` line and exit 0.
2. Confirm Step 4 prints `CONFLICT (content): Merge conflict in recipe.txt` and
   the three marker lines (`<<<<<<<`, `=======`, `>>>>>>>`).
3. Confirm Step 5's resolved file shows `milk: 2 cups buttermilk` and **no**
   marker lines.
4. Confirm Step 6's graph shows a `|\` diamond with a
   `Merge branch 'feature-blueberries'` node.
5. Run the tests (next section) — all checks must pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `10 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in CI. It needs no network.

## Cleanup

Nothing to clean up. Every script works inside its own temporary directory and
removes it on exit (`trap cleanup EXIT`). No files are written outside that
directory, and your global git configuration is never touched.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md): older git without `git switch`,
reading and removing conflict markers, `git merge --abort` when you want to
start over, and why nothing persists after the script finishes.

## Security notes

See [security.md](security.md). Short version: temp directory only, no network,
a local-only `.invalid` git identity, no `sudo`, and short scripts you should
read before running.

## Extension exercises

1. **Keep only one side.** Re-run the conflict, but resolve it by keeping only
   `main`'s line (or only the feature's). Note how `git log --graph` looks
   identical — resolution content does not change the shape of history.
2. **Abort instead of resolve.** After the conflict appears, run
   `git merge --abort` and confirm with `git status` that the working tree
   returned to its pre-merge state.
3. **Force a fast-forward to fail.** Add a commit on `main` before merging a
   branch, then try `git merge --ff-only BRANCH`. Explain why git refuses.
4. **Visualize differently.** Run
   `git log --graph --oneline --decorate --all` and identify every branch
   pointer and the merge commit in the output.

## Navigation

- **Previous day:** Day 30 — Git Fundamentals: Repositories, Staging, and
  Commits (`labs/sections/computing-foundations/day-030-git-fundamentals-repositories-staging-and-commits/`).
- **Next day:** Day 32 — Remotes and GitHub
  (`labs/sections/computing-foundations/day-032-remotes-and-github/`).
