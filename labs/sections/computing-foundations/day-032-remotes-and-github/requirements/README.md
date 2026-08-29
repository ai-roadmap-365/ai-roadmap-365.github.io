# Dependencies — Day 032 lab

**Only Git and a POSIX shell.** This lab has zero installable dependencies
and needs no account, no network, and no API key:

- `git` (2.28 or newer recommended, for `git init -b main`; an older-Git
  fallback is documented in `troubleshooting.md`).
- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distro).
- Standard OS utilities: `mktemp`, `rm`, `ls`, `sed`, `grep` — all part of
  the base system.

## Do I need a GitHub account?

**No.** The whole point of this lab is to teach remotes *truthfully without a
network*: the "remote" is a **bare repository** in a temporary folder on your
own disk, and every `git` command is exactly the one you would run against a
hosting platform.

A **real** push to a hosting platform additionally needs two things this lab
deliberately does not require, both covered conceptually in the lesson:

1. **An account** on a platform (such as GitHub, GitLab, or Bitbucket).
2. **Authentication** — either an HTTPS **personal access token** or an
   **SSH key pair**. You never use your account password directly, and you
   never put a token or password in the remote URL.

When you are ready to try a real remote, create a repository on the platform,
copy the address it gives you, and run the same `git remote add` / `git push`
commands from this lab against that address instead of a folder path.
