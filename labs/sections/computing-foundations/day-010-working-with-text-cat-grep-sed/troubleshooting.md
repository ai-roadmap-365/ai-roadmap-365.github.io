# Troubleshooting — Day 010 lab

## `No such file or directory` for the log

The scripts find the log **relative to their own location**, so run them from
the lab directory as shown in the README (`bash examples/analyze_log.sh`). If
you copied a pipeline out on its own, point it at the real path:
`examples/samples/access.log`. Confirm the file is there with
`ls examples/samples/`.

## `awk: syntax error` or the wrong column comes out

`awk '{print $1}'` prints field **1**; the fields are separated by spaces.
In this log field 1 is the IP, field 7 is the path (e.g. `/index.html`), and
field 9 is the status code (e.g. `200`). If you get the wrong value, you
probably used the wrong field number — recount from the left, starting at 1.

## My 404 count is 0 (or far too high)

Two common causes:

- You matched the wrong field. Use `awk '$9 == 404'` — the `$9 == 404`
  compares the status field to the number 404.
- You used `grep 404` without spaces and matched a **byte size** or timestamp
  that happens to contain "404". Anchor to the status column instead, or use
  `grep ' 404 '` (with surrounding spaces) as a quick approximation.

## `uniq` didn't remove duplicates

`uniq` only collapses **adjacent** identical lines, so you must `sort` first.
The correct order is always `sort | uniq` (or `sort | uniq -c` to count).
`sort -u` does both in one step.

## The top-IP rows come out in a different order than the sample

Two IPs tie at 5 requests each. `sort` on macOS (BSD) and Linux (GNU) may
order tied rows differently. This is expected and harmless — the top IP and
every count are still identical, and the tests only check those. See
`expected-output/FIELDS.md`.

## `Permission denied` when running a script

Run it through bash explicitly: `bash tests/run_tests.sh`. You do not need to
`chmod +x` anything. If you prefer `./tests/run_tests.sh`, first run
`chmod +x tests/run_tests.sh`.

## `bash: command not found` on Windows

Use WSL (`wsl --install`, then open Ubuntu). PowerShell does not have these
Unix text tools.
