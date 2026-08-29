# Troubleshooting — Day 035 lab

## `git: command not found`

Git is not installed or not on your `PATH`. See `requirements/README.md` for
install instructions, then re-run. Confirm with `git --version`.

## `error: unknown switch` or `git switch` not recognized

Your git is older than 2.23. Either update git, or replace `git switch -c NAME`
with `git checkout -b NAME` and `git switch NAME` with `git checkout NAME` in
the scripts — the behavior is identical.

## `Author identity unknown` / a commit is refused

Git needs a name and email to record a commit. The scripts set a **local**
identity inside the temporary repo:

```bash
git config user.name  "Workflow Learner"
git config user.email "learner@example.invalid"
```

These writes go only into the temp repo's `.git/config` — they never change
your global identity. If you copied commands out of order and skipped these
two lines, the first commit will fail; run them (inside the repo) first.

## The merge fast-forwards and no merge commit appears

You omitted `--no-ff`. Without it, git slides `main` forward and the branch
shape disappears from the log. Always use `git merge --no-ff ...` when you want
the merge recorded as a distinct commit (the shape of a merged pull request).

## `git tag` prints nothing

Either the tag command did not run, or you created it in a way that did not
persist. Re-run the annotated form and confirm:

```bash
git tag -a v1.0.0 -m "First release"
git tag
```

## Annotated vs lightweight tags

- **Lightweight** (`git tag v1.0.0`): just a name pointing at a commit. No
  author, date, or message.
- **Annotated** (`git tag -a v1.0.0 -m "..."`): a full object storing the
  tagger, date, and message. **Use annotated tags for releases.**

Inspect the difference with `git show v1.0.0` (an annotated tag shows the
tagger and message header; a lightweight tag jumps straight to the commit).

## Deleting a tag

If you tagged the wrong commit or chose the wrong version:

```bash
git tag -d v1.0.0                 # delete the local tag
git push origin :refs/tags/v1.0.0 # delete it on a remote you already pushed to
```

Then re-create the tag on the correct commit. (In this lab the "remote" is the
local bare `origin`, so the second command works offline too.)

## The starter script errors out on `git log`

That is expected **while exercises are unfilled**: with the placeholders in
place, no commits are made, so `git log` has nothing to show. Complete the five
exercises (replace every `__FILL_ME_IN__` line) and the script runs cleanly.
The test detects the placeholders and checks the starter's structure only until
you finish.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open your Linux distribution and follow the
Linux path). These are bash scripts; native PowerShell is not supported here.
