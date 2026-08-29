# Security notes — Day 012 lab

- **What the scripts do:** `backup_notes.sh` reads a directory listing and
  prints a summary. It only *reads* file names and metadata — it never opens,
  executes, moves, or deletes the files it finds. It makes **no network
  connections**, writes **no files**, and changes **no settings**. The test
  suite writes only to a temporary directory created with `mktemp -d` and
  deletes it automatically.

- **Never runs untrusted input as commands.** The script treats its argument
  purely as a directory path and the file names purely as data. Because every
  variable expansion is quoted (`"${target}"`, `"${path}"`), a file named with
  spaces or shell metacharacters cannot be turned into extra commands — quoting
  is the security boundary here, not just a style choice.

- **Privileges:** everything runs as your normal user. Nothing in this lab needs
  `sudo`. If any tutorial ever tells you to `sudo` a shell script you have not
  read, that is your cue to stop and read it first.

- **Reading before running:** both scripts are short and commented — read them
  before you run them. Piping a script off the internet straight into the shell
  (`curl … | bash`) hands a stranger the power to run any command as you; this
  course's habit is that every lab script is small enough to read and understand
  before executing.

- **Optional ShellCheck:** running the optional ShellCheck linter is itself a
  security practice — it flags unquoted variables and other patterns that turn
  data into unintended commands.
