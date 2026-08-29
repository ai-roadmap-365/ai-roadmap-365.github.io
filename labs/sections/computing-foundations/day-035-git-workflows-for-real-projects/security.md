# Security notes — Day 035 lab

- **Everything happens in a temporary directory.** Both scripts create their
  repositories under a `mktemp` directory (for example
  `/tmp/day035-demo.XXXXXX`) and delete it on exit via a `trap`. Nothing is
  written to your home directory, your existing repositories, or anywhere
  permanent.
- **No network, no account, no keys.** The "origin" is a **local bare
  repository** in that same temp directory. The scripts make no network calls
  and need no credentials, so there is nothing to leak.
- **Your global git identity is untouched.** The scripts set `user.name` and
  `user.email` with a repository-**local** `git config` inside the temp repo.
  Your machine's global git configuration is never read or modified.
- **The `.env` demonstration is a teaching prop.** The scripts create a fake
  `.env` file containing an obviously non-real value to show that `.gitignore`
  keeps it out of git. It is never committed and is destroyed with the temp
  directory. This mirrors the real rule: **never commit secrets** — exclude
  them with `.gitignore`, because anything committed lives in history forever,
  even after a later deletion.
- **Read before you run.** Both scripts are short and commented. Reading a
  script before executing it is a habit this course reinforces; you can see
  exactly what these do (create files, make commits, delete a temp dir).
