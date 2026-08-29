# Troubleshooting — Day 036 lab

## `No such file or directory` when running a script

You are not in the lab directory. Change into it first, then run the command:

```bash
cd labs/sections/computing-foundations/day-036-choosing-and-configuring-a-code-editor
bash examples/editorconfig_demo.sh
```

## `Permission denied` when running the script

Run it through bash explicitly rather than as `./examples/...`:

```bash
bash examples/editorconfig_demo.sh
```

That avoids needing the executable bit. If you prefer `./examples/...`, first
run `chmod +x examples/editorconfig_demo.sh`.

## The checker reports no violations at all

The sample files or the `.editorconfig` were not created. Re-run the demo from
a clean state and confirm it prints the `Wrote .editorconfig` line before the
checking section. If you are running the **starter**, make sure you have
completed Exercise 1 (the six `.editorconfig` rules) — an empty rule set means
nothing to check against.

## `command not found: awk` (or `grep`, `mktemp`)

These ship with macOS and every mainstream Linux distribution. If one is
missing you are on an unusually stripped-down system (a minimal container, for
example) — install the base utilities (`apt install coreutils gawk grep` on
Debian/Ubuntu) and retry.

## The tests say a starter check failed

Search your `starter/editorconfig_demo.sh` for the word `FILL-IN`: any that
remain mark an unfinished exercise. Complete all four, save, and re-run
`bash tests/run_tests.sh`. If Exercise 3 is wrong, the "after the fix" line
will still report a violation instead of `OK` — re-read the exact `printf`
line named in the exercise comment.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and follow the commands unchanged).
The plain Windows Command Prompt and PowerShell do not run these bash scripts.

## The temporary path in the output looks different from the sample

That is expected. The path after `Created sample project in:` is a fresh
`mktemp` directory, so it differs on every run and machine. Only that one line
varies; see `expected-output/FIELDS.md`.
