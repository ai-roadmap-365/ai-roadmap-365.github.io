# Judge the Source Before the Data — the nine exercises

Today's lab is not about the shape of a dataset. It is about deciding
**whether a source deserves the hour you are about to spend on it**, and
about the handful of client behaviours — pagination, backoff, caching,
checksums — that make working with a live source safe and reproducible
rather than fragile and rude.

Five files sit in this directory:

| File | What it is |
| --- | --- |
| `mock_server.py` | A mock API on `127.0.0.1` and an ephemeral port: a paginated dataset, a rate-limited endpoint, and an ETag-aware resource. Infrastructure, not an exercise |
| `datasource.py` | The client and judgement functions your exercises test. Read this first |
| `fixtures.py` | The two `unemployment_rate` dictionaries and series, and the good/deficient source metadata used below |
| `conftest.py` | Two server fixtures: `mock_api` (relents after 2 requests) and `stubborn_mock_api` (relents after 10 — more than any test's budget) |
| `test_datasource.py` | Your nine exercises. Each currently calls `pytest.skip` |

Replace each `pytest.skip(...)` with real assertions, and delete the skip
line. Run `pytest starter -v` as often as you like. Never run
`pytest examples starter` in one command — both directories hold a module
named `test_datasource.py`, and pytest aborts collection on the clash. Run
the two directories as two separate commands.

The mock server is started and stopped inside each fixture. When the
suite finishes, no port is bound and no process from this lab is left
running.

---

## Exercise 1 — the definition trap

`fixtures.unemployment_series_a()` and `unemployment_series_b()` are two
columns both called `unemployment_rate`, both `float64`, with overlapping
ranges. `datasource.naive_join_check` — the dtype-and-range check most
people would actually run — passes on both. `datasource.dictionary_aware_join_check`
reads the two dictionaries' *prose definitions* instead, and refuses the
join. This is the day's centrepiece: prove the naive check passes and the
dictionary-aware check does not, on the same two columns.

## Exercise 2 — pagination to exhaustion

`datasource.fetch_all_pages` follows the mock API's `has_more` flag rather
than a page count you supply. Prove the assembled row count equals
`mock_server.TOTAL_ROWS`, that the row ids arrive in order, and that the
number of requests the server logged for `/dataset` matches how many
pages it actually took to cover `TOTAL_ROWS` at `PAGE_SIZE` per page.

## Exercise 3 — rate limiting

`datasource.fetch_with_backoff` retries a `429` with a bounded, growing
delay. Against `mock_api` (relents after 2 rejections), prove it succeeds
on the third attempt and that the server's own log of rejected attempts
is `[1, 2]`. Against `stubborn_mock_api` (relents after 10, more than any
sane budget), prove that calling it with `max_attempts=3` raises
`datasource.RateLimitExceeded` rather than retrying forever, and that it
made exactly 3 attempts — no more.

## Exercise 4 — conditional request

`datasource.fetch_with_etag` sends `If-None-Match` on the second call for
a path it has already cached. Prove the first call is not served from
cache and downloads real bytes; prove the second call **is** served from
cache, returns the same body, and — because a `304` carries no body — costs
zero bytes over the wire. Report the byte counts in your assertions, not
just booleans.

## Exercise 5 — checksum pinning

Write a small CSV to `tmp_path`, compute its SHA-256 with
`datasource.sha256_of`, and assert it equals a value you compute once
(with `hashlib.sha256(...).hexdigest()`, not by guessing) and record here.
Then change a single byte in a copy of the file and assert the checksum
changes. "Downloaded from X" is not reproducible. "Downloaded from X,
checksum `4c0610aa...`" is.

## Exercise 6 — the five-minute source assessment

`datasource.assess_source` takes a metadata dict and returns a
`SourceVerdict`: what granularity, coverage and licence were stated,
whether a dictionary exists, and a list of everything missing. Run it on
`fixtures.GOOD_SOURCE_METADATA` and assert `.ready` is `True` with no
problems. Run it on `fixtures.DEFICIENT_SOURCE_METADATA` and assert
`.ready` is `False`, with the specific missing items named in `.problems`.

## Exercise 7 — the licence gate

`datasource.check_licence` returns `{"allowed": bool, "reason": str}` —
never a bare boolean. Assert `CC0` is allowed for redistribution, and that
`"All rights reserved"` is refused with a reason that names why. A licence
permitting *analysis* is not the same permission as one permitting
*republishing the data* — the reason string is where that distinction
lives.

## Exercise 8 — coverage check

`datasource.check_coverage` compares a dictionary's `expected_regions`
against the keys a dataset actually delivers. Run it against
`fixtures.NATIONAL_DATASET_KEYS`, which is missing one of the four
expected regions, and assert the gap is detected by name — `"west"` — not
merely flagged as "incomplete".

## Exercise 9 — provenance record

`datasource.record_provenance(url, checksum, retrieved_at=...)` returns a
dict with exactly `url`, `retrieved_at` and `sha256`. Call it twice with
the **same** injected timestamp and assert the two records are equal —
regenerating from the same fixture is stable once the clock is pinned.
That is the honest way to test something that includes "now" without the
test becoming flaky: hold the clock still rather than asserting on a
moving target.
