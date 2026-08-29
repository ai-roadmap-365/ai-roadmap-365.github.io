# Required output lines (all platforms)

A correct run of `backup_notes.sh DIRECTORY` prints, in order:

1. `=== Notes summary ===`
2. `Directory: <the directory you passed, or . for the default>`
3. `Total files: <count of regular files at the top level>`
4. `By extension:`
5. One indented line per extension, `  <ext>: <count>`, in sorted order —
   or `  (none)` when the directory holds no files.
6. `=== End of summary ===`

Rules the counts must obey:

- Only **regular files** at the top level are counted; subdirectories are
  skipped, and the script does not descend into them.
- Files with no dot in the name (such as `README`) are grouped under
  `(no extension)`, which sorts before lettered extensions because it begins
  with `(`.
- Extensions keep their original case (`photo.JPG` counts as `JPG`, not `jpg`).
- Hidden files whose names begin with a dot (such as `.gitignore`) are not
  matched by the `*` glob and are therefore not counted.

Error and edge cases:

- Passing a path that is not a directory prints `Error: '<path>' is not a
  directory` to **standard error** and exits with code `1`.
- An empty directory prints `Total files: 0` and `  (none)`, and exits `0`.

`sample-run.txt` in this directory is a real captured run against
`examples/sample-notes/` on macOS (Apple Silicon, bash 3.2.57, 2026-07-12).
Linux output is identical for the same inputs, since the script uses only
portable commands.
