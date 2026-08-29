# Troubleshooting — Day 012 lab

## `syntax error near unexpected token 'done'` or `'fi'`

An `if` needs `; then` after its condition, and a `for`/`while` needs `do`
after its header. A missing one of these confuses the shell until it reaches
the matching `done`/`fi`. Compare your file line by line against
`examples/backup_notes.sh`.

## `backup_notes.sh: line N: target: unbound variable`

You are running under `set -u` (strict mode) and referenced a variable that was
never assigned — almost always a typo in the name (`${targett}` instead of
`${target}`). That is strict mode doing its job: fix the spelling.

## `command not found` right after an assignment

You put spaces around the `=`. Shell assignment must have **no spaces**:
`total=0`, never `total = 0`. With spaces, the shell tries to run a command
called `total`.

## The counts look wrong

- **A subdirectory got counted.** It should not — the loop uses `[ -f "${path}" ]`
  to keep only regular files. Make sure you did not change that test to `-e`.
- **A file with a space in its name broke the count.** You have an unquoted
  variable. Every expansion must be quoted: `"${target}"/*`, `"${path}"`.
- **`.gitignore` and other dotfiles are missing.** That is expected: the `*`
  glob does not match names beginning with a dot, so hidden files are not
  counted.

## Comparing numbers behaves oddly

Use integer operators for numbers: `[ "${total}" -eq 0 ]`, `-gt`, `-lt`.
Reserve `=` for string comparison. `[ "${total}" = 0 ]` compares text, which
can surprise you when the value is empty or has leading spaces.

## `Permission denied` when running the script

You do not need to make the file executable — run it through bash explicitly:
`bash starter/backup_notes.sh`. If you prefer `./starter/backup_notes.sh`,
first run `chmod +x starter/backup_notes.sh`.

## The starter prints `Total files: 0` even though the directory has files

That is the starting state: the loop body is a no-op (`:`) until you complete
Exercise 4, and `target` is hard-coded until you complete Exercise 1. Finish
the exercises in order and the counts appear.

## Windows: `bash` is not recognized

Install WSL (`wsl --install`), open the Ubuntu terminal, and run the Linux
commands there. Native Windows PowerShell uses a different scripting language
not covered by this lab.
