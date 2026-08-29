# Expected output — Day 079 lab

Every file here is a real capture from the authoring machine (macOS 26.5.1,
Apple Silicon, Python 3.14.0, beautifulsoup4 4.15.0, requests 2.34.2,
pytest 9.1.1, bash 3.2.57, 2026-07-19). Nothing in this lab reaches the
internet: the only server involved is started by the lab itself, listens on
127.0.0.1, and serves the files in `examples/fixtures/`.

## Files

- `test-run.txt` — a full `bash tests/run_tests.sh`: 51 checks, 0 failures,
  exit 0.
- `sample-run.txt` — `python3 examples/demo.py catalogue.csv` end to end:
  robots.txt parsed, links sorted by permission, a cold-cache crawl, a
  warm-cache re-run, the CSV, and the server's own access log.
- `regex-vs-parser.txt` — `python3 examples/regex_vs_parser.py`: the naive
  regular expression finds 10 names, three of them wrong or unusable;
  BeautifulSoup finds all 12 correctly.
- `catalogue.csv` — the 12-row CSV the demo writes. Line endings are CRLF,
  which is what the `csv` module produces by default and what RFC 4180 asks
  for.

## The one line that changes between runs

`test-run.txt` contains, in section 1:

```
  ok: two fixture servers get two different ephemeral ports ( 55118 55119 )
```

Those two numbers are **assigned by the operating system at run time** and will
differ on your machine and between your own runs. That is the check passing,
not the check drifting: the whole point is that the lab never claims a fixed
port such as 8000 and therefore never collides with anything you already have
running. Every other line in every file here is byte-identical run to run.

## What the numbers mean

| Number | Where it comes from |
| --- | --- |
| 12 items | 4 rows on each of the 3 catalogue pages |
| 1 item with no price | `NAV-003 Brass Compass` on page 2 has no `td.price` element at all |
| 3 page requests, first run | `/catalogue/page-1.html`, `-2`, `-3`; the crawl stops because page 3 has no `a.next` |
| 0 page requests, second run | every page came from the on-disk cache |
| 1 request on the second run | `/robots.txt`, deliberately never cached — permission is re-checked, never remembered |
| 0 requests for `/private/internal-notes.html` | robots.txt disallows it; the link is present on page 1 and the server would serve it |
| `[1.0, 1.0, 1.0]` sleeps | the `Crawl-delay: 1` declared in the fixture robots.txt, one per real fetch |
| 10 vs 12 names | the naive regex misses 2 rows outright and mangles 2 more |
| 34 passed | the pytest suite in `tests/test_scraper.py` against `examples/` |
| 1 passed on the starter | `RobotsPolicy.load` is left worked as a model; the six exercises are not |

## Two User-Agent strings in the demo's closing log

`sample-run.txt` ends with two distinct User-Agent strings. That is expected.
Section 1 of the demo loads robots.txt a second time under the name
`GreedyBot` in order to show that a site can publish different rules for
different clients, and the fixture robots.txt refuses `GreedyBot` everything.
Your own scraper sends exactly one User-Agent, and the harness asserts that
separately.

## Platform notes

- macOS and Linux produce identical bytes. The lab uses only `http.server`,
  `threading` and `socket` behaviour that is the same on both.
- On Windows, run everything inside WSL. The captured files contain em dashes
  and a `&` decoded from `&amp;`; a terminal set to a legacy code page may
  render those as replacement characters while the data itself stays correct.
- `catalogue.csv` has CRLF line endings. `wc -l` still reports 13; a text
  editor set to strict LF may show a trailing `^M` on each line. Both are the
  file being correct.
- If your machine has an HTTP proxy configured through `HTTP_PROXY` or
  `ALL_PROXY`, `requests` may try to send even 127.0.0.1 traffic through it.
  `troubleshooting.md` covers the fix.
