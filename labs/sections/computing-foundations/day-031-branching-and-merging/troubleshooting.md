# Troubleshooting — Day 031 lab

## `git: 'switch' is not a git command`

Your git predates version 2.23 (August 2019). `git switch` and `git restore`
are the modern spellings; the classic `git checkout` still does everything:

- `git switch -c NAME`  →  `git checkout -b NAME`  (create and move onto a branch)
- `git switch NAME`     →  `git checkout NAME`      (move onto an existing branch)

The scripts use `git switch`; either upgrade git or apply these substitutions.

## Reading the conflict markers

When a merge conflicts, git rewrites the file with three marker lines around
the clashing region:

```text
<<<<<<< HEAD
milk: 1 cup buttermilk       <- the version already on your current branch (main)
=======
milk: 2 cups                 <- the version coming from the branch you are merging
>>>>>>> feature-blueberries
```

To resolve: **delete all three marker lines** (`<<<<<<<`, `=======`,
`>>>>>>>`) and edit what remains until the file reads exactly the way you want
— which may be one side, the other, or a blend of both. Then `git add` the
file and `git commit`. The conflict is only "resolved" once no marker lines
remain; `grep -n '^<<<<<<<\|^=======\|^>>>>>>>' FILE` finds any you missed.

## I panicked and want to start the merge over

A conflicted merge is completely reversible until you commit it:

```text
git merge --abort
```

This throws away the half-finished merge and returns the working tree to
exactly how it was before you ran `git merge`. Nothing is lost. Then you can
try again when ready.

## "You have not concluded your merge (MERGE_HEAD exists)"

Git is reminding you that a merge is still in progress. Either finish it
(`git add` the resolved files, then `git commit`) or cancel it
(`git merge --abort`). You cannot switch branches mid-conflict.

## The graph doesn't show a `|\` diamond

You probably got a **fast-forward** instead of a three-way merge — the two
branches had not truly diverged, so git just slid the pointer forward and no
merge commit was created. A diamond only appears when both branches added
commits after they split. Step 4 of the lab forces divergence on purpose;
Step 7 shows the fast-forward case for contrast.

## `nothing to commit, working tree clean` when you expected a conflict

The branches did not actually change the same lines, so git merged them
automatically. Make sure both edits touch the **same line** of `recipe.txt`.

## Nothing appears to persist after the script finishes

That is by design. Each script works inside a temporary directory that is
deleted on exit (the `trap cleanup EXIT` line). To keep a repository around
and poke at it yourself, create your own directory and run the git commands
there by hand.
