# Troubleshooting — Day 029 lab

## `git: command not found`

Git is not installed. It is free on every platform — see
`requirements/README.md` for the one-line install for macOS, Linux, and
Windows. Confirm with `git --version`.

## `Author identity unknown` or git asks for your name and email

Git needs an author name and email to make a commit, and this appears when
you have never set a global identity. **The lab scripts avoid this entirely**
by setting a *local* identity inside the temporary repository only:

```bash
git config user.name "Course Learner"
git config user.email "learner@example.com"
```

Because there is no `--global`, your own machine's configuration is never
touched. If you run git commands by hand in your own test folder and hit this
message, set a local identity the same way (inside that repo), or set a global
one if you are ready: `git config --global user.name "Your Name"`.

## `git restore: unknown command` or `unknown option`

Your git predates `git restore` (added in git 2.23). The scripts already fall
back to `git checkout <commit> -- notes.txt`, which does the same job on older
git. If you are typing commands yourself, use the `git checkout` form.

## The temporary directory seems to still be there

The scripts delete their temporary directory on exit via a `trap`, including
on normal completion and on errors. If you pressed Ctrl-C in the middle of a
step, a leftover folder may remain — its path is printed near the top of the
output as `(temporary directory: ...)`. Delete it with `rm -rf <that path>`.
The scripts never write anywhere except that one temporary directory.

## The commit ids do not match the sample output

That is expected and correct. A commit's identifier is a hash of its content,
author, and time, so it differs every run and on every machine. Only the
messages and the overall structure should match `expected-output/sample-run.txt`.

## `Permission denied` when running a script

Run it through bash explicitly rather than as an executable:
`bash examples/history_demo.sh`. If you prefer `./examples/history_demo.sh`,
first make it executable with `chmod +x examples/history_demo.sh`.

## Windows: `bash` is not recognized

Use Git Bash (installed with Git for Windows) or WSL (`wsl --install`, then
open your Linux distribution and follow the Linux path). The scripts are
plain POSIX shell and run unchanged in both.
