# Week 05 project — Versioned Notes Repository

This week you learned git end to end: why version control exists, the core
model, branching and merging, remotes, pull requests, undoing mistakes, and
real workflows. This project turns your own course notes into a properly
versioned, collaboration-ready repository.

## What you are building

A git repository for your notes (your notes from this course are perfect)
that demonstrates every core git skill: a clean history, branches, a merge,
a resolved conflict, a recovered mistake, and — if you have a GitHub account
— a remote and a merged pull request. If you don't want to use GitHub, a
local bare "remote" (Day 32's technique) satisfies the remote requirement.

## Requirements

Show each of this week's skills at least once:

- **Init + commits** (Days 29–30): `git init`, a `.gitignore`, and several
  atomic commits with good messages.
- **Branching + merging** (Day 31): a `feature` branch merged back to `main`.
- **A resolved conflict** (Day 31): deliberately create and resolve one.
- **A remote** (Day 32): push to GitHub *or* a local bare repo.
- **A pull request** (Day 33): open and merge one on GitHub, *or* rehearse
  the PR flow locally (branch → diff → --no-ff merge) if offline.
- **An undo/recovery** (Day 34): use `git revert` or recover a commit with
  `git reflog`.
- **A tagged release** (Day 35): tag a milestone `v1.0.0` with `git tag -a`.

## Steps

1. `git init` a notes repo; add a `.gitignore`; make several atomic commits.
2. Create a `feature` branch, add content, and merge it back.
3. Deliberately create a conflict (edit the same lines on two branches) and
   resolve it.
4. Add a remote (GitHub or a local bare repo) and push.
5. Open and merge a PR (GitHub) or rehearse the flow locally.
6. Practice one undo: `git revert` a commit, or `reset --hard` then recover
   via `git reflog`.
7. Tag `v1.0.0`.
8. Validate against the checklist below.

## Expected output

- `git log --graph --oneline --decorate` shows a clean history with at least
  one branch merge and the `v1.0.0` tag.
- The history includes a merge commit whose conflict you resolved.
- A remote is configured (`git remote -v`) and your commits are pushed.
- You can point to the commit you reverted or recovered.

## Validation

- [ ] `.gitignore` present and excluding the right files (no secrets, no
      build junk).
- [ ] At least 5 atomic commits with clear messages (Conventional Commits a
      plus).
- [ ] A `feature` branch was merged into `main`.
- [ ] One conflict was created and resolved (a merge commit proves it).
- [ ] A remote exists and your commits are pushed to it.
- [ ] One undo/recovery performed (`revert` or `reflog` recovery).
- [ ] A `v1.0.0` annotated tag exists.

## Troubleshooting

- No GitHub account / offline? Use a local bare repo as the remote (Day 32)
  and rehearse the PR flow locally (Day 33) — both fully satisfy the
  requirements.
- Stuck in a conflict? `git status` shows the conflicted files; edit the
  markers, `git add`, then `git commit`. `git merge --abort` backs out.
- Dropped a commit with `reset --hard`? `git reflog` lists recent HEAD
  positions; `git reset --hard <hash>` brings it back (Day 34).
