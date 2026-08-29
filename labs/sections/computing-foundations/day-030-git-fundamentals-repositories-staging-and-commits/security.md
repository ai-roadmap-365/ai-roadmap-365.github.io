# Security notes — Day 030 lab

- **Everything happens in a throwaway directory.** Each script creates its own
  temporary repository with `mktemp -d` **inside this lab directory**
  (`.gitdemo.XXXXXX` / `.gittest.XXXXXX`) and deletes it on exit via a shell
  `trap`. Nothing is created outside that temp directory, and no existing repo
  of yours is touched.

- **Local identity only.** The scripts set `user.name` and `user.email` with
  per-command `-c` flags, so they never write to your global `~/.gitconfig`
  and never change how commits are authored in your real projects. The email
  used, `learner@example.invalid`, is in the reserved `.invalid` domain and can
  never resolve to a real address.

- **No network, no privileges.** Git here runs entirely offline: the repo has
  no remote, nothing is pushed or fetched, and no command needs `sudo`. If a
  tutorial ever tells you to `sudo` a Git command you have not read, stop.

- **Never commit secrets — and preview `.gitignore` for them.** The lab makes
  this concrete: it writes a fake `secret.key` and uses `.gitignore` to keep it
  untracked, so it is never captured in a commit. In real work, credentials
  (API keys, tokens, passwords, `.env` files) must be listed in `.gitignore`
  *before* the first `git add`, because once a secret is committed it lives in
  the repository history even after you delete the file — removing it later
  requires rewriting history. The habit to build: before you commit, run
  `git status` and read what is staged, and keep a `.gitignore` that excludes
  every secret and credential file. `git check-ignore -v <file>` confirms a
  file is being ignored before you trust it.

- **Read scripts before running them.** Both lab scripts are short and
  commented. Reading a shell script before executing it is a habit worth
  keeping for anything you download.
