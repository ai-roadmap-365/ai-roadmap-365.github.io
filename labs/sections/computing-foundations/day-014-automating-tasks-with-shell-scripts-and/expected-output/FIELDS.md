# Expected output — what a correct run produces

The captures in this directory are real runs of `examples/organize_files.sh`
on the authoring machine (macOS, Apple Silicon, 2026-07-12). Paths were
rewritten to `~/organize-demo` for readability; everything else is verbatim.

## Files here

- `sample-dry-run.txt` — a real `--dry-run` on a folder of five mixed files:
  one "would create directory" line per new extension, one "would move" line
  per file, and a summary ending in `0 changes made`. The folder is left
  untouched.
- `sample-real-run.txt` — a real run (files sorted into `pdf/`, `txt/`, `jpg/`,
  `csv/`, `zip/`), a second run proving idempotency (`0 file(s) organized`),
  and the resulting `organize.log`.

## Invariants a correct run must satisfy (every platform)

1. Dry-run mode prints `[dry-run]` lines and makes **no changes** — no files
   moved, no subfolders created, no log written.
2. A real run moves each file into a subfolder named for its **lowercased**
   extension (so `photo.JPG` and `photo.jpg` both go to `jpg/`).
3. Each real move appends one timestamped line to `organize.log`.
4. A second real run on the same folder moves nothing and reports
   `0 file(s) organized` (idempotency).
5. The script exits `0` on success and touches nothing outside the target
   directory — in particular it never edits any crontab or scheduler.

## Platform differences

The script uses only POSIX shell features plus `tr`, `mv`, `mkdir`, `basename`,
and `date`, all present on macOS and every mainstream Linux distribution, so
output is identical across them apart from the absolute paths shown. The line
order follows the shell's alphabetical glob expansion, which is consistent on a
given system. On Windows, run it inside WSL for identical behavior.

## Automated test output (captured 2026-07-12, macOS)

```text
18 checks, 0 failure(s).
```
