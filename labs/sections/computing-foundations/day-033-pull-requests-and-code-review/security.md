# Security notes — Day 033 lab

- **What the scripts do:** create a *throwaway* Git repository in a temporary
  directory (`mktemp -d`), make a few commits, run diffs and merges, and print
  the results. They make **no network connections** and need **no elevated
  privileges**.
- **Temporary directory only:** all work happens inside a fresh temp directory,
  which the reference and starter scripts delete on exit (the test harness sets
  `PR_FLOW_KEEP=1` to inspect the repo, then removes it itself). Nothing is
  written into your project, your home directory, or any existing repository.
- **Your global Git config is untouched:** the scripts set the commit identity
  (`user.name`, `user.email`) **locally, inside the throwaway repo only**, using
  a placeholder address (`learner@example.com`). Your own `git config --global`
  settings are never read or changed.
- **No credentials, no remotes:** the lab never authenticates, never adds a
  remote, and never pushes. There is nothing to leak. When you later open a
  *real* pull request, treat the diff and every comment as permanent and
  potentially public — never paste secrets, API keys, or personal data into
  them.
- **Reading before running:** both scripts are short and commented — read them
  first. Running unread shell scripts is a common way developers get
  compromised; every lab script in this course is small enough to read and
  understand before executing.
