# Troubleshooting — Day 033 lab

## `git: command not found`

Git is not installed. On macOS, `xcode-select --install` provides it; on
Debian/Ubuntu, `sudo apt install git`; on Fedora, `sudo dnf install git`.
Verify with `git --version`.

## `fatal: not a git repository`

You tried to run a Git command outside the throwaway repo. Run
`examples/pr_flow.sh` (or `starter/pr_flow.sh`), which creates and enters the
temp repo for you. If you are experimenting by hand, `cd` into the temp path
the script printed at the top of its output.

## `Please tell me who you are` / `empty ident name`

Git has no commit identity configured. The scripts set one *locally* inside the
throwaway repo, so this should not happen when you run them. If you are working
by hand, set it in that repo only:

```bash
git config user.email "you@example.com"
git config user.name "Your Name"
```

Using `git config` without `--global` scopes it to the current repository and
leaves your global settings alone.

## `git: 'switch' is not a git command`

Your Git predates version 2.23 (August 2019), when `switch` was added. The
scripts fall back to `git checkout` automatically. If you are typing commands
yourself, use `git checkout -b feature` to create a branch and
`git checkout main` to move between them — the effect is identical.

## The merge did not create a merge commit

You merged without `--no-ff` while `main` had not moved, so Git
"fast-forwarded" and left no merge point. Redo it with
`git merge --no-ff feature`. A pull-request merge always records a merge
commit; `--no-ff` (no fast-forward) is how you force one locally.

## `sed: -i may not be used with stdin` or an unexpected `notes.md.bak` file

The scripts use `sed -i.bak` (with a backup suffix) specifically so the same
command works on both macOS (BSD `sed`) and Linux (GNU `sed`), then delete the
`.bak` file. If you adapted the command and dropped the suffix, restore it:
`sed -i.bak 's/old/new/' notes.md && rm -f notes.md.bak`.

## Git shows the graph lines differently than the sample

Terminal width and font can shift where the `|\` and `|/` connector lines sit
in `git log --graph`. The important thing is the two-parent **merge commit**,
not the exact spacing. The tests check the merge structure, not the glyphs.

## `Permission denied` when running a script

Run it through bash explicitly: `bash examples/pr_flow.sh`. If you prefer
`./examples/pr_flow.sh`, first `chmod +x examples/pr_flow.sh`.
