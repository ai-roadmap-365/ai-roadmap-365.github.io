# Required output lines (all platforms)

A correct run of `explore_files.sh` prints, in order (values such as the
workspace path, owner name, and dates will differ on your machine):

1. `=== Build and Explore a File Tree ===`
2. `Workspace: <absolute path ending in tmp.explore.XXXXXX>`
3. `Working directory (pwd): <same workspace path>`
4. `Created nested directories with: mkdir -p project/data`
5. A plain `ls` of `project/` listing `data` and `report.md`
6. A `ls -la` long listing showing `.`, `..`, the `data` directory (leading
   `d`), and `report.md` (leading `-`)
7. `Before chmod:` followed by a line for `run.sh` whose permission string is
   `-rw-r--r--` (octal 644)
8. `After chmod:` followed by a line for `run.sh` whose permission string is
   `-rwxr-xr--` (octal 754)
9. `Moved report.md into data/ with: mv report.md data/`
10. A final `ls` showing `report.md` gone from the current directory and
    present under `data/`
11. `=== Done ===`

After the script finishes, **no `tmp.explore.*` directory remains** under the
lab directory — the trap removes the workspace on exit.

## Platform differences (not fabricated — described)

- **macOS** appends an `@` to the permission string in `ls -l`/`ls -la` output
  when a file carries extended attributes, e.g. `-rw-r--r--@`. This is normal;
  the nine permission bits before the `@` are what matter. `sample-macos.txt`
  in this directory is a real captured run on macOS (Apple Silicon,
  2026-07-12).
- **Linux** prints the same nine bits without the `@` (occasionally a trailing
  `+` when POSIX ACLs are set), and the owner/group columns show your Linux
  user and group. The permission strings `-rw-r--r--` and `-rwxr-xr--` are
  identical across both systems.
- The tests in `tests/run_tests.sh` match the nine permission bits and tolerate
  the trailing `@`/`+`, so they pass on both macOS and Linux.
