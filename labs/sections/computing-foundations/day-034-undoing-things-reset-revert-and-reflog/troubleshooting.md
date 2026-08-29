# Troubleshooting — Day 034 lab

## "I ran `git reset --hard` and my commits are gone!" — reflog to the rescue

This is the headline skill of the whole lesson: they are almost certainly
**not** gone. A hard reset moved the branch pointer, but the commits are still
in the object store and still listed in the reflog. Run:

```bash
git reflog
```

Find the line describing where you were *before* the reset (often
`HEAD@{1}`), copy its hash, and restore:

```bash
git reset --hard <that-hash>
```

Your commits reappear, because each commit points to its parent, so restoring
the newest one brings the whole chain back. This works for weeks after the
mistake, until Git's garbage collection eventually prunes unreachable commits.

## `git restore: command not found` or `unknown option`

`git restore` was added in Git 2.23 (August 2019). On an older Git, use the
classic equivalents: `git reset HEAD <file>` to un-stage, and
`git checkout -- <file>` to discard a working-tree change. Upgrading Git is
the cleaner fix; `git --version` shows what you have.

## `You are in 'detached HEAD' state`

You checked out a commit hash directly instead of a branch, so `HEAD` points
at a commit rather than a branch, and new commits here belong to no branch.
This is safe as long as you do not commit and wander off. To get back onto a
branch, run `git switch main` (or `git checkout main`). If you *did* commit in
detached HEAD and want to keep it, create a branch first:
`git branch keep-this <hash>`.

## `--hard` warning: it discards uncommitted work

`git reset --hard` and `git restore` overwrite your working files. Any change
you have **not committed** is not a snapshot and is **not** in the reflog, so
it cannot be recovered. Before any hard reset, run `git status` to see what is
uncommitted, and `git stash` (or a quick commit) to protect anything you might
still want. The lab scripts only ever touch a throwaway temp repo, so you are
safe practising there — build the habit before you use these commands on real
work.

## `Please tell me who you are`

Git needs a name and email to make a commit. The lab scripts set a **local**
identity inside the throwaway repo so your global config is untouched. If you
are running commands by hand in your own scratch repo, run:

```bash
git config user.email "you@example.com"
git config user.name "Your Name"
```

## `fatal: not a git repository`

You are not inside a Git repository. `cd` into the directory the script
created (or into any repo) before running Git commands. The lab scripts handle
this for you by creating and entering a temp directory automatically.

## The starter script prints "NOT YET"

That is the built-in check telling you an exercise is unfinished. Search the
starter for the `REPLACE THIS LINE` and `PLACEHOLDER` markers and complete
each `# TASK:` with the exact command named in its comment, then re-run.
