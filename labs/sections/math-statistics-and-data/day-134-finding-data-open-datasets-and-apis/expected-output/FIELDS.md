# What in `expected-output/` is exact, and what can legitimately differ

Captured from a real run on 2026-08-20: macOS, Python 3.14.0, pandas
3.0.5, pytest 9.1.1, inside this lab's own `.venv`.

## Exact everywhere (these never change on a correct implementation)

- `38 checks, 0 failure(s)` as the harness's final line, and `exit=0`.
- `9 passed` for `pytest examples`, `9 skipped` for `pytest starter`
  (untouched checkout).
- The checksums in Exercise 5: `4c0610aa92b75ca794ceec30068934fc6bc3d2fbff87969a15977f8fcf96f13f`
  for `id,value\n1,10\n2,20\n3,30\n` and
  `9352ed755477b7af1eefd6e473c3880dd49e0a5d368846f51f8d96519d2bcf50` for the
  same content with `3,31` in place of `3,30`. SHA-256 of fixed bytes is
  deterministic on any machine.
- `rows_fetched=25`, `dataset_requests_made=3` (`TOTAL_ROWS=25`,
  `PAGE_SIZE=10`, so pages 1, 2, 3 with the last partial).
- `relenting_attempts=3`, `relenting_rejections_logged=1,2` (the mock's
  `rate_limit_trigger_count=2` by construction).
- `stubborn_attempts_made=3` (the client's own `max_attempts=3` in that
  call; the stubborn mock's trigger count of 10 is never reached).
- `first_fetch_bytes=92` -- the byte length of `mock_server.ETAG_BODY`,
  which is a fixed JSON literal and therefore a fixed length. If this
  module's payload text is ever edited, this number moves with it.
- `second_fetch_bytes=0` -- a 304 response has no body, always.
- `coverage_missing=west` -- `fixtures.NATIONAL_DATASET_KEYS` is a fixed
  set missing exactly one of `fixtures.DICTIONARY_A`'s four
  `expected_regions`.
- `deficient_problem_count=5` -- `fixtures.DEFICIENT_SOURCE_METADATA`
  states only `granularity`, so five of the six checks in `assess_source`
  fire.

## Machine-dependent or environment-dependent

- `python`, `pandas`, `pytest` version strings in section 1 -- pinned in
  `requirements/requirements.txt`; a mismatch is reported, not fatal to
  the nine exercises.
- Wall-clock timing lines pytest prints (`in 0.38s` and similar) -- never
  asserted on anywhere in this lab.
- The exact ephemeral port each mock server binds -- read back from the
  operating system every run and never hard-coded or compared.

## Deliberately not asserted, and why

- `provenance_stable_with_pinned_clock` is asserted only when the caller
  passes the same fixed `retrieved_at` to both calls. Two calls without an
  injected timestamp will differ in `retrieved_at` and that is correct,
  not a bug -- the harness does not compare those, because the real clock
  advancing is not a failure.
- Byte-for-byte identity of anything downloaded from a real, live API is
  never claimed by this lab. Everything measured here is against the
  bundled mock, which is the only source whose exact bytes this repository
  controls.
