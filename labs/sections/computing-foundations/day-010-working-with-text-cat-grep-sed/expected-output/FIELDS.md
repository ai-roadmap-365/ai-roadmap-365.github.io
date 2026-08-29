# Expected output — Day 010 lab

The sample log (`examples/samples/access.log`) is fixed and committed, so the
numbers below are **exact and reproducible** on every platform.

## Captured runs in this directory

- `analyze_log.txt` — a real run of `bash examples/analyze_log.sh` (macOS,
  2026-07-12). The `Log file:` line is shown as a relative path for
  portability; on your machine it prints the absolute path to the sample.
- `run_tests.txt` — a real run of `bash tests/run_tests.sh` with the starter
  still unfinished (absolute lab path shortened to `<lab>`).

## The known-correct answers

| Question | Answer |
| --- | --- |
| Total requests | 40 |
| Top IP address | `10.0.0.14` |
| Top IP request count | 10 |
| 404 responses | 7 |
| Unique paths | 13 |
| Status 200 responses | 29 |

These are the values `tests/run_tests.sh` asserts. If your pipelines print
anything different, a stage is wrong — re-read the exercise comment.

## Platform notes (macOS vs Linux)

- `wc`, `sort`, `uniq`, `awk`, `grep`, and `sed` ship with both macOS (BSD
  versions) and Linux (GNU versions). Every command in this lab uses only
  options common to both, so the counts are identical.
- **Tie-breaking in the top-IP list is the one place output can differ.** Two
  IPs (`192.168.1.23` and `192.168.1.10`) each appear 5 times. When counts
  tie, BSD `sort` and GNU `sort` may order those two rows differently. This
  never affects the top IP (`10.0.0.14`, 10 hits) or any count — only the
  relative order of the two five-hit rows. The tests check counts and the top
  entry, not the order of tied rows, so both platforms pass.
