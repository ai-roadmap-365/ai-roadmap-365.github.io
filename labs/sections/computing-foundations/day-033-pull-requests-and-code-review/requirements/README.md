# Dependencies — Day 033 lab

**One dependency: Git.** This lab simulates the pull-request workflow with
local branches only, so it needs nothing beyond a shell and Git:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution)
- `git` ≥ 2.0 (2.23 or newer preferred, so `git switch` is available; the
  scripts fall back to `git checkout` on older versions)
- Standard OS utilities: `mktemp`, `sed`, `printf` — all part of the base
  system on macOS and Linux.

There is no `requirements.txt`/`package.json` here; the scripts install
nothing.

## About a *real* pull request

A genuine pull request lives on a hosting platform (such as GitHub or GitLab)
and therefore needs, in real life:

- a free account on the platform, and
- network access to push a branch and open the request in the browser or with
  the platform's command-line tool.

This lab deliberately needs **neither**. Because a pull request is review and
merge gates wrapped around Git branches and merges, you can rehearse the entire
logic offline with the tools above. The lesson covers the account-and-network
side conceptually; you will open a real pull request in the Week 5 project.
