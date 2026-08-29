# Troubleshooting — Day 041 lab

## The hook does not run — my bad commit went through

A git hook only runs if it is **executable**. If you installed the hook by
copying a file, make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

Then stage and commit again. This is the single most common hook problem: git
silently ignores a non-executable hook and does not warn you. The lab's demo and
tests set `chmod +x` for you; you only hit this when installing a hook by hand.

## `git commit --no-verify` skipped my hook — is that a bug?

No. `--no-verify` deliberately bypasses `pre-commit` and `commit-msg` hooks. It
exists for genuine emergencies (for example, committing a work-in-progress fix
while a hook is temporarily broken). **Avoid it as a habit**, because the whole
point of the hook is to run every time: skip it routinely and broken changes
slip through exactly when you are in a hurry and most likely to make mistakes.
This is also why teams back a local hook with CI — CI runs on a shared server
and cannot be skipped with `--no-verify`, so it catches what a bypassed hook
missed.

## `command not found: git`

Install git (see `requirements/README.md`): macOS `xcode-select --install`;
Debian/Ubuntu `sudo apt install git`. Verify with `git --version`.

## `mktemp: illegal option` or a temp-directory error

The scripts try `mktemp -d` first and fall back to `mktemp -d -t hookdemo` for
older/BSD variants. If both fail, your `mktemp` is unusual — set a temp dir
manually and re-run, or run inside WSL on Windows.

## The pipeline never fails

`pipeline.sh` only fails when you name the stage to fail as its first argument:
`bash examples/pipeline.sh test` fails at `test`. With no argument, every stage
passes and it exits 0 — that is the intended "all green" run.

## My commit is blocked but I cannot see any trailing whitespace

Trailing whitespace is invisible by design. Show it with `grep -nE '[ \t]+$'
yourfile.sh`, or configure your editor to reveal or strip trailing whitespace on
save. The hook is catching real characters at the ends of lines.

## Windows: `bash` is not recognized

Use WSL: run `wsl --install`, open Ubuntu, and follow the Linux instructions.
Native PowerShell is not supported for this lab because git hooks here are shell
scripts.
