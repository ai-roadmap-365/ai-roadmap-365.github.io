# What must be true, and what may vary

Everything in this directory was captured from a real run on the authoring
machine (macOS 26.5.1 on Apple Silicon, Python 3.14.0, pytest 9.1.1,
bash 3.2.57, 2026-07-19). Absolute paths were rewritten to `<repo>`,
`<tmpdir>` and `/tmp/reports` so nothing about one machine leaks into the
files; nothing else was edited.

## Required behaviour — the same on any POSIX machine

| Behaviour | Required value |
| --- | --- |
| `pytest examples -q` | `61 passed`, exit 0 |
| `pytest starter -q` (as shipped) | `1 passed, 8 skipped`, exit 0 |
| `bash tests/run_tests.sh` | `56 checks, 0 failure(s).`, exit 0 |
| First `job.py run` | `"action": "written"`, exit 0 |
| Second `job.py run`, same date | `"action": "skipped"`, exit 0, and the file's `generated_at` is still the first run's |
| Report files after two runs | exactly one `report-YYYY-MM-DD.json` |
| Leftover `*.partial` files | none, ever |
| `job.py run` while the lock is held | exit **75**, `"status": "already-running"`, and **no** output file written |
| `job.py run --simulate-failure` | exit **1**, `"error": "RuntimeError"` |
| `job.py run --simulate-hang 30 --timeout 1` | exit **124**, `"error": "JobTimeout"`, finishes in about a second |
| `supervise.py --timeout 1 -- sleep 30` | exit **124**, no surviving `sleep` process |
| `job.py watch` with a fresh heartbeat | `OK: ...`, exit 0 |
| `job.py watch` with a stale heartbeat | `STALE: ... the job has stopped running`, exit 1 |
| `job.py watch` with no heartbeat at all | `MISSING: ...`, exit 1 |
| Generated cron line | parses to `30 2 * * *`; next runs 2026-07-19 02:30 and 2026-07-20 02:30 UTC |
| Generated systemd timer | contains `OnCalendar=*-*-* 02:30:00` and `Persistent=true` |
| Generated launchd plist | contains `Hour` 2, `Minute` 30, and `RunAtLoad` false |

## The report's numbers, which you can check by hand

For 2026-07-19, `examples/data/readings.csv` holds six rows:

- ALPHA 16.8, 18.0, 19.6 → count 3, min 16.8, max 19.6, mean 18.13
  (54.4 ÷ 3 = 18.1333…, rounded to 18.13)
- BRAVO 20.2, 26.4 → count 2, min 20.2, max 26.4, mean 23.3
- CHARLIE 31.7 → count 1, min = max = mean = 31.7

`reading_count` is therefore 6.

## Daylight saving, from the operating system's own time zone database

| Case | Required result |
| --- | --- |
| 2026-03-08 02:30 `America/New_York` | does not exist; resolves to 07:30 UTC, which is 03:30 EDT locally |
| 2026-11-01 01:30 `America/New_York` | happens twice: 05:30 UTC (EDT) and 06:30 UTC (EST) |
| Daily 12:00 local across 2026-03-08 | one 23-hour gap |
| Daily 12:00 local across 2026-11-01 | one 25-hour gap |
| Daily 12:00 UTC, any week | every gap exactly 24 hours |

## Drift, which is arithmetic and therefore exact

| Loop | Gap between runs | Lateness of run 100 |
| --- | --- | --- |
| `work(); sleep(60)` with 5 s of work | 65 s | 495 s |
| sleep until the next deadline | 60 s | 0 s |

## What legitimately varies

- **Timings.** "the whole suite runs in 0.54s", the `0.20s` of real time in
  section 5 of `demo.py`, and the seconds reported by `run_tests.sh` all
  depend on the machine. Only the assertions about them ("under 10 seconds",
  "under a second, not thirty") are required.
- **Temporary paths.** Every run uses a fresh `mktemp -d` directory, so the
  paths in the captures are not reproducible and were rewritten anyway.
- **Process ids** inside `daily-report.lock`.
- **`duration_seconds` in the log.** With `--now` the clock is frozen, so it
  is `0.0` in every capture here. Under a real clock it is the true duration.
- **The order of `ok:` lines** is fixed, but the exact wording of a `FAIL:`
  line includes the value that was seen, which differs per failure.

## What must never appear

- Any entry in the user's real crontab, `~/Library/LaunchAgents`, or
  `~/.config/systemd/user` — checked directly by section 8 of the runner.
- Any surviving `hold_lock.py`, `job.py` or `sleep` process after the suite
  finishes — also checked by section 8.
- Any network connection. Section 10 asserts that no networking module is
  imported anywhere in `examples/` or `starter/`.
