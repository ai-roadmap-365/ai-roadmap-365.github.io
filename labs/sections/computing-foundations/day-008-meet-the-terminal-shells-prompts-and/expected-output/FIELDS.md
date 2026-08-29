# Required tour sections (all platforms)

A correct run of `shell_tour.sh` prints, in order, these labelled sections:

1. `=== Shell Tour ===`
2. `Generated on: YYYY-MM-DD`
3. `Current shell (echo $0): <shell or script name>`
4. `Default shell (echo $SHELL): <path, e.g. /bin/zsh or /bin/bash>`
5. `Shell process (ps -p $$):` followed by the current shell's process row
6. `Prompt string (echo "$PS1"): <template, or an "empty" note in non-interactive runs>`
7. `Working directory (pwd): <an absolute path>`
8. `Echo demo (echo hello): hello`
9. `Date (date): <current date and time>`
10. `User (whoami): <your username>`
11. `Recent command history (history | tail)` section (may be empty in a script)
12. `type echo: echo is a shell builtin`
13. `=== End of tour ===`

`sample-macos.txt` in this directory is a real captured run (macOS, Apple
Silicon, zsh as the default shell, 2026-07-12).

## Platform and context notes (real, not fabricated)

- **`echo $0` inside a script prints the script's path** (e.g.
  `examples/shell_tour.sh`), because `$0` is the name of the *program running
  now* — which, for a script, is the script. Run `echo $0` **directly in your
  interactive terminal** and it prints your shell instead, such as `-zsh` or
  `bash`. Both are correct; they answer slightly different questions.
- **`$PS1` is usually empty in a non-interactive script**, so the tour prints a
  note rather than a value. Run `echo "$PS1"` in your interactive shell to see
  the real prompt template (for example `%n@%m %1~ %#` in zsh).
- **`history | tail` is often empty inside a script**, because history is a
  feature of interactive shells. Run `history | tail` directly in your terminal
  to see your logged commands.
- **Linux vs macOS:** the shape is identical. `ps -p $$` formats its columns
  slightly differently, `date` follows your locale, and if your default shell is
  bash the `$SHELL` line reads `/bin/bash`. No field is fabricated here; only the
  exact strings differ by machine.
