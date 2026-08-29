# Dependencies — Day 018 lab

**Just `curl`, which is already installed.** This lab has one tool dependency
and it ships with your OS:

- `curl` — the command-line HTTP client. Preinstalled on macOS and on every
  mainstream Linux distribution. Check with `curl --version`.
- `bash` ≥ 3.2 and the standard `grep` — also part of the base system.

If `curl` is somehow missing (rare, or a minimal container), install it with
the Day 13 package manager:

- macOS: `brew install curl`
- Debian/Ubuntu: `sudo apt install curl`
- Fedora: `sudo dnf install curl`

**Optional:** HTTPie (`http`) is the friendlier client shown in the lesson.
Install it with `brew install httpie` or `sudo apt install httpie` if you want
to try it — it is not required for any exercise or test.

There is no `requirements.txt`/`package.json`: the lab needs no language
runtime, only `curl` and a network connection.
