# Troubleshooting — Day 030 lab

## `git: command not found`

Git is not installed (or not on your `PATH`). Install it — see
`requirements/README.md` — and confirm with `git --version`.

## `*** Please tell me who you are` / "identity not set"

When you run `git commit` in your own repositories, Git needs a name and email
for the commit's author fields. If you have never configured them, Git stops
and asks. **This lab's scripts never hit that error** because they pass a
local identity on every command:

```bash
git -C "${work}" \
  -c user.name="Day 30 Learner" \
  -c user.email="learner@example.invalid" \
  ...
```

The `-c key=value` flags set config for that single command only, so nothing
is written to your global `~/.gitconfig`. In your *own* projects you would
instead set it once, globally:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## `nothing to commit, working tree clean`

This is not an error — it is Git telling you there is **nothing staged**.
`git commit` only records what is in the staging area. If you edited a file
but did not `git add` it, the staging area is empty and there is nothing to
commit. Run `git status`: if your change shows under "Changes not staged for
commit", `git add` it first, then commit. This is the single most common
beginner surprise, and the lesson's three-areas model explains exactly why.

## `secret.key` shows up in `git status` anyway

The `.gitignore` step failed. Common causes:

- The file was **already tracked** before you added it to `.gitignore`. Git
  ignores *untracked* files only; a file already committed keeps being
  tracked. Untrack it with `git rm --cached secret.key`, then commit.
- The pattern does not match. Confirm `.gitignore` contains exactly
  `secret.key` (no trailing spaces). Ask Git why with
  `git check-ignore -v secret.key` — it prints the matching rule, or nothing
  if no rule matches.

## `Permission denied` when running a script

Run it through bash explicitly rather than executing it directly:

```bash
bash examples/git_basics.sh
```

If you prefer `./examples/git_basics.sh`, first `chmod +x` the script.

## A `.gitdemo.*` or `.gittest.*` directory is left behind

The scripts delete their throwaway repo on exit via a `trap`. A leftover only
happens if a run was killed (e.g. Ctrl-C at just the wrong moment). It is
safe to delete by hand: `rm -rf .gitdemo.* .gittest.*` from the lab directory.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open your Linux distribution) and follow the
Linux path, or use Git Bash, which ships with Git for Windows.
