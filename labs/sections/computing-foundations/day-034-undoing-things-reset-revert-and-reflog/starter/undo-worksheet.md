# Undo and Recover — Day 034 worksheet

Fill this in as you complete the five exercises in `undo_recover.sh` (or as
you run the reference in `examples/undo_recover.sh`). Keep it — the Week 5
project (a versioned notes repository) expects you to demonstrate a clean
recovery, and this is your rehearsal.

## 1. What `git commit --amend` changed

| | Before amend | After amend |
| --- | --- | --- |
| Commit message (subject) |  |  |
| Commit hash (short) |  |  |

One sentence: why did the hash change even though I only edited the message?

>

## 2. `git reset --soft` versus `git reset --hard`

For each mode, record what happened to your **staged changes** (the index)
and your **edited files** (the working tree).

| Reset mode | What happened to staged changes | What happened to edited files |
| --- | --- | --- |
| `git reset --soft HEAD~1` |  |  |
| `git reset --hard HEAD~1` |  |  |

One sentence: which mode is safe to run with uncommitted work you care about,
and which one would destroy it?

>

## 3. The reflog hash I recovered

- Commit count **before** the disaster (`git reset --hard HEAD~2`): __________
- Commit count **after** the disaster: __________
- The reflog line I recovered from (paste it): 

  ```
  
  ```

- The exact command I ran to recover: 

  ```
  
  ```

- Commit count **after** recovery: __________

One or two sentences: why did restoring to that single commit bring back the
*whole* chain of commits, not just one?

>

## One thing that surprised me

One or two sentences.
