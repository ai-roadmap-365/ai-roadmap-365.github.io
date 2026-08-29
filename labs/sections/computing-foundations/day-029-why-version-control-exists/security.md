# Security notes — Day 029 lab

- **Where the scripts operate:** each script works only inside a *temporary
  directory it creates itself* with `mktemp`, and deletes that directory on
  exit (via a `trap`, including on errors and interrupts). It writes nothing
  outside that one folder and leaves no repository behind on your machine.
- **No global configuration is changed.** The scripts set the git author name
  and email *locally* inside the temporary repository only (no `--global`), so
  your own git configuration is never modified. This is the safe pattern: a
  throwaway repo can have a throwaway identity.
- **No network, no privileges.** Every operation is local git work. The
  scripts make no network connections, need no `sudo`, and require no account
  or API key. If any tutorial ever asks you to `sudo` a script you have not
  read, stop and read it first.
- **No secrets committed.** The demo commits only a tiny plain-text file it
  writes itself. This is also the lesson's own security rule in practice:
  never commit passwords, API keys, or personal data — a repository's history
  keeps everything ever committed, so a leaked secret must be rotated, not
  merely deleted in a later commit.
- **Reading before running:** both scripts are short and commented — read them
  first. Running unread shell scripts is one of the most common ways
  developers get compromised; every script in this course is small enough to
  read and understand before you execute it.
