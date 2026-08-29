# Security notes — Day 036 lab

- **What the scripts do:** create a handful of tiny text files in a **temporary
  directory** (made with `mktemp`), write an `.editorconfig`, read the files
  back with `awk`/`grep`/`tail`, print a report, and delete the temporary
  directory on exit. They make **no network connections**, need **no elevated
  privileges**, and write **nothing** outside that self-deleting temp dir.
- **Temp dir only:** all file creation happens under your system temp location
  (`$TMPDIR` or `/tmp`). The scripts never touch your home directory, the
  repository, or any project of yours. A `trap ... EXIT` removes the temp
  directory even if the script is interrupted.
- **Privileges:** everything runs as your normal user. Nothing here needs
  `sudo`; if any tutorial ever asks you to `sudo` a script you have not read,
  that is your cue to stop and read it first.
- **Reading before running:** both scripts are short and commented — read them
  before running. Running unread shell scripts is a common way developers get
  compromised, and this course's habit is that every lab script is small
  enough to read and understand first.
