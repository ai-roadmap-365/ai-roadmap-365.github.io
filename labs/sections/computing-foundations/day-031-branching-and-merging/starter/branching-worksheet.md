# Branching worksheet — Day 031

Fill this in from your own run of `starter/branch_merge.sh` (after you have
completed the five exercises) or from your own hand-typed experiment. Keep it —
Week 5's project (the Versioned Notes Repository) reuses exactly these moves.

## Branches I created

| Branch name | Created with (command) | What I changed on it |
| ----------- | ---------------------- | -------------------- |
|             |                        |                      |
|             |                        |                      |

## The merge I performed

| Question | My answer |
| -------- | --------- |
| Which branch did I merge INTO? |  |
| Which branch did I merge IN? |  |
| Was it a **fast-forward** or a **three-way** merge? |  |
| How do I know? (merge commit created? `|\` diamond in the graph?) |  |

> Reminder: a **fast-forward** happens when the target branch has not moved
> since you branched, so git just slides its pointer forward — no merge commit.
> A **three-way merge** happens when both branches advanced, so git builds a
> new merge commit with two parents (and may hit a conflict on the way).

## The conflict I resolved

Paste the exact conflict block git wrote into the file (the three marker lines
and the two competing versions between them):

```text
<<<<<<< HEAD

=======

>>>>>>>
```

- The version above `=======` came from branch: ____________________
- The version below `=======` came from branch: ____________________
- The resolution I chose (kept theirs / kept mine / blended both): ___________
- The final line I committed: ____________________________________________

## One sentence: why did this conflict happen?

_(Hint: what did the two branches both do to the same line?)_
