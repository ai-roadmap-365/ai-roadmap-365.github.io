# Security notes — Day 043 lab

- **What the scripts do:** create a Python virtual environment inside a
  throwaway temporary directory, print which interpreter is active, write a
  small `requirements.txt`, then deactivate and delete the temp directory. They
  make **no network connections**, need **no elevated privileges**, and write
  nothing outside their own temp folder.

- **Temp directory only.** All work happens in a directory created by `mktemp`
  and removed on exit (even if a step fails, via a cleanup trap). Nothing is
  written into your project or your home directory, so there is nothing to
  accidentally commit from this lab.

- **Never commit a virtual environment.** In your own projects, add `.venv/` to
  `.gitignore`. A committed venv is large, machine-specific, and can leak local
  paths; the correct thing to share is the `requirements.txt` recipe.

- **Pin your dependencies.** When you start installing real packages from PyPI,
  record exact versions (`pip freeze > requirements.txt`, which writes lines
  like `requests==2.32.3`). Pinning is a security practice as well as a
  reproducibility one: it stops an unexpected or tampered newer version from
  being pulled in silently under a name you already trust. Install only packages
  you mean to, and watch for typo-squatted names (e.g. `reqeusts` for
  `requests`).

- **Read before you run.** Both scripts here are short and commented — read them
  first. Running unread shell scripts is a common way developers get
  compromised; every script in this course is small enough to read before
  executing.
