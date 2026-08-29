# Security notes — Day 008 lab

- **What the scripts do:** read information about your current shell session
  (`echo $0`, `echo $SHELL`, `ps -p $$`, `echo "$PS1"`) and run a few read-only
  commands (`pwd`, `echo`, `date`, `whoami`, `history`, `type`). They make **no
  network connections**, write **no files**, and change **no settings**.
- **Privileges:** everything runs as your normal user. Nothing in this lab needs
  `sudo`; if any tutorial ever asks you to `sudo` a script you haven't read, that
  is your cue to stop and read it — a habit this course reinforces, because a
  shell runs whatever you type with your full privileges and asks no questions.
- **Privacy:** a shell profile (username, working directory, shell version) is
  mildly identifying. Sharing it in a class forum is normally fine; avoid posting
  profiles of employer-managed machines. Remember that your shell records a
  **history file** on disk — so never type passwords or secret keys directly on a
  command line, where they would be logged in plain text.
- **Reading before running:** both scripts are short and commented — read them
  first. Running unread shell scripts from the internet is one of the most common
  ways developers get compromised; the course's rule is that every lab script is
  small enough to read and understand before executing.
