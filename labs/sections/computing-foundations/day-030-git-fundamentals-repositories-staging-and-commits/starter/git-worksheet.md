# Git worksheet — Day 030

Fill this in from a real run of `examples/git_basics.sh` (or your finished
`starter/git_basics.sh`). Watch the output scroll past and record what you
actually saw — the point is to connect each command to the state it produced.

## 1. The state of `notes.txt` at each stage

For each moment, write what `git status --short` showed (or would have shown)
for `notes.txt`, and say which of the three areas held the current version.

| Moment | `git status --short` code | Which area holds the newest content |
| --- | --- | --- |
| Right after creating the file, before `git add` | `______` | working directory only |
| After `git add notes.txt`, before commit | `______` | ______ |
| Right after the first `git commit` | (clean / no entry) | ______ |
| After appending a second line, before staging | `______` | ______ |
| After staging and the second `git commit` | (clean / no entry) | ______ |

Reminder of the codes: `??` = untracked, `A ` = staged new file,
` M` = modified but not staged, `M ` = modified and staged.

## 2. Your two commit hashes (short form)

Copy the short hashes the script printed (yours will differ from anyone
else's — that is expected; a hash is computed from the snapshot's content,
author, time, message, and parent).

- First commit  ("Add notes.txt with initial notes"): `_______`
- Second commit ("Append a second line to notes.txt"): `_______`
- Which commit does `HEAD` point at after the run? `_______`

## 3. What `.gitignore` excluded

- The file name listed inside `.gitignore`: `______________`
- The file that stayed **untracked** because of it: `______________`
- Did that ignored file ever appear in `git status`? (yes / no): `______`
- One sentence in your own words on why keeping secrets out of a repository
  matters:

  `___________________________________________________________________`

## 4. One thing that surprised you

`_____________________________________________________________________`
