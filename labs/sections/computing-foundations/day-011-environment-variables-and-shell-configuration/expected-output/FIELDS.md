# Required output fields (all platforms)

A correct run of `examples/inspect_env.sh` prints, in order:

1. `=== Environment Inspection ===`
2. `HOME:  <absolute path>`
3. `USER:  <your login name>`
4. `SHELL: <path to your login shell>` (often `/bin/zsh` or `/bin/bash`)
5. `LANG:  <locale>` (for example `en_US.UTF-8`; may read `C.UTF-8` or be empty on minimal systems)
6. `PATH directories (one per line):` followed by one `  - <dir>` line per entry
7. `PATH contains <n> directories.`
8. `--- Subshell variable demo ---`
9. `  child process sees demo_var = hello from a subshell` (the exported value reached the child)
10. `  after subshell, demo_var = '<empty, did not leak>'` (the variable did **not** escape the subshell)
11. `--- Alias demo ---` then `  alias greet ran: hello`
12. `--- Command resolution ---` then the resolved path of `ls` and the note that `cd` is a builtin
13. `=== End of inspection ===`

## About the captured sample

`sample-macos.txt` is a real run captured on macOS (Apple Silicon, zsh,
2026-07-12). It was captured with a **representative five-directory PATH** so
the list stays readable; a real developer machine usually has a longer PATH,
and the `PATH contains <n> directories` count will be higher. Every other line
is exactly what the script prints.

## Platform differences

- **Linux:** identical shape. `SHELL` is commonly `/bin/bash`; `type cd` still
  reports a shell builtin; `command -v ls` resolves to `/usr/bin/ls` or
  `/bin/ls` depending on the distribution.
- **Windows:** run under WSL, where output matches Linux. Native PowerShell is
  not supported by this bash script.
- No field may read `<unset>` on a normally configured interactive machine,
  though `LANG` can legitimately be empty in a bare container.
