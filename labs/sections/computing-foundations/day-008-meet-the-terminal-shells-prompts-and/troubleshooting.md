# Troubleshooting — Day 008 lab

## `echo $0` prints the script name, not my shell

That is correct. `$0` is the name of the program running *right now*; inside a
script that program is the script, so you see `examples/shell_tour.sh` or
`starter/shell_tour.sh`. To see your interactive shell, type `echo $0` **directly
in your terminal** (not through the script) — it will print something like
`-zsh` or `bash`.

## `echo "$PS1"` prints an empty line (or the tour says "empty")

`PS1`, the prompt-string template, is normally only set in interactive shells,
so a script usually sees it empty — the tour prints a note instead of a value.
Run `echo "$PS1"` in your interactive terminal to see the real template (for
example `%n@%m %1~ %#` in zsh). Keep the double quotes; without them the shell
may mangle the special characters.

## `history | tail` shows nothing

`history` is a feature of *interactive* shells; a script often starts with an
empty history list, which is why the tour prints a placeholder note. Run
`history | tail` directly in your terminal after running a few commands and you
will see your logbook.

## `Permission denied` when running the script

You don't need to make it executable — run it through bash explicitly:
`bash starter/shell_tour.sh`. If you prefer `./starter/shell_tour.sh`, first run
`chmod +x starter/shell_tour.sh`.

## Tests fail on a field that is still `unknown`

That check is telling you an exercise is unfinished — search the starter for
`"unknown"` and complete the remaining assignments, replacing each with the
command named in its comment, wrapped in `$(...)`.

## `ps -p $$` looks different from the sample

Column formatting and the `TTY` value vary by OS and by how you launched the
shell; the important part is that a single process row for your current shell
appears. This is expected and not a failure.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and run the scripts unmodified), or
skip the script and type the individual commands from the lesson's hands-on
section in your terminal, filling the worksheet manually.
