# Troubleshooting — Day 011 lab

## `echo "$PATH"` prints a literal `$PATH`

You are in a context that does not expand variables, or you used single
quotes. In bash or zsh, use double quotes: `echo "$PATH"`. Inside single
quotes the shell does not substitute variables.

## The alias in the script did not run (`greet: command not found`)

By default bash does not expand aliases in a non-interactive script. The
scripts here fix this with `shopt -s expand_aliases` near the top, and define
the alias on its own line before calling it. If you write your own script,
include that line, and remember an alias must be defined on a line *before*
the line that uses it.

## `DEMO_VAR` / `demo_var` is still set after the subshell

You ran the `export` outside the parentheses. The whole point of the
`( ... )` wrapper is to confine the variable to a child shell. Keep the
assignment and `export` inside the parentheses; after the subshell exits the
variable is gone, which the script confirms with the `after subshell` line.

## `command -v` prints nothing for a command

That command is genuinely not on your `PATH`. Try one you know exists
(`command -v ls`) to confirm the tool works. If a tool you just installed is
not found, its directory is probably missing from `PATH`, or the shell has
cached an old location — open a new terminal, or run `hash -r`.

## Spaces around `=` cause an error

`NAME = value` is not an assignment; the shell tries to run a command called
`NAME`. Always write `NAME=value` with no spaces around the equals sign.

## `bash -c` inside the subshell shows an empty value

You set the variable but did not `export` it, so the child `bash -c` process
did not inherit it. Add `export demo_var` before the `bash -c` line.

## Windows: `bash` is not recognized

Install WSL (`wsl --install`), open the Ubuntu terminal, and run the scripts
there. Native PowerShell is a different shell and is not supported by these
bash scripts. You can still inspect variables in PowerShell with
`Get-ChildItem Env:` and `$Env:PATH`, but the lab scripts expect bash.
