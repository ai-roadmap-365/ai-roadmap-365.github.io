# Security notes — Day 009 lab

- **Where the scripts write.** Both `examples/explore_files.sh` and
  `starter/explore_files.sh` write **only** inside a single temporary
  directory they create with `mktemp -d` *under this lab directory* (named
  `tmp.explore.XXXXXX`). They `cd` into it, build a small tree of empty files
  there, and nowhere else. A `trap cleanup EXIT` removes that directory when
  the script finishes, fails, or is interrupted, so the lab **leaves nothing
  behind**. Nothing outside the workspace is created, modified, or deleted.
- **No network, no privileges.** The scripts make no network connections,
  need no `sudo`, and change no system settings. Everything runs as your
  normal user on files your user owns.
- **About `rm -rf` in general.** The cleanup step uses `rm -rf` on the exact
  workspace path the script itself just created — a safe, bounded use. In
  general, though, `rm -rf` is the most dangerous command a beginner runs: it
  deletes an entire directory tree immediately, with no Trash and no undo, and
  a wrong or mistyped path (especially one beginning with `/`, or one built
  from an empty variable) can erase far more than intended. The habits that
  keep you safe: read any `rm -rf` command in full before pressing Return,
  confirm the target with `pwd`/`ls` first, never run it on a path you have
  not verified, and be extra careful when the path comes from a variable in a
  script. In this lab the target is fixed and self-created, which is exactly
  the kind of bounded use that is safe.
- **Read before running.** Both scripts are short and commented — read them
  first. Running unread shell scripts is a common way developers get
  compromised; every lab script in this course is small enough to read and
  understand before executing.
