# Security notes — Day 034 lab

- **What the scripts do:** create a small Git repository in a **temporary
  directory** (via `mktemp`), run local Git commands against it, and delete
  the directory on exit. They make **no network connections**, need **no**
  elevated privileges, and write **nothing** outside that temp directory.
- **Temp dir only:** every operation is confined to a throwaway repo, so
  practising destructive commands here cannot harm any real project. This is
  deliberate — the safest way to learn `git reset --hard` is on a repository
  you do not care about.
- **`--hard` discards uncommitted work:** the one genuinely destructive move
  in this lesson. On a real repository, `git reset --hard` and `git restore`
  overwrite your working files, and uncommitted changes are gone with no undo
  and no reflog entry. Always `git status` first, and **commit or `git stash`
  before running `--hard`** on anything you might still want.
- **Local identity, not global:** the scripts set `user.email` and
  `user.name` **locally** inside the temp repo, so your global Git identity is
  never modified.
- **Reading before running:** both scripts are short and commented — read them
  first. Running unread shell scripts is a common way developers get burned;
  the course's rule is that every lab script is small enough to read and
  understand before executing.
