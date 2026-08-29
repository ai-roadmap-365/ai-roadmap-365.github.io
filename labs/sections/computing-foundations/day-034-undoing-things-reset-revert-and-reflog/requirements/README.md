# Dependencies — Day 034 lab

**Only Git and a POSIX shell.** This lab has zero installable dependencies
beyond tools you already have from the Git section:

- `git` (2.23 or newer recommended, so that `git restore` is available;
  every command was verified on git 2.50.1). Check yours with `git --version`.
- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution).
- Standard utilities: `mktemp`, `rm`, `tail` — all part of the base system.

No network access is required and no API key is needed: every operation runs
against a throwaway local repository created in a temporary directory. If
`git restore` is unavailable on an older Git, the lesson and troubleshooting
notes give the equivalent `git reset HEAD <file>` and `git checkout -- <file>`
commands.
