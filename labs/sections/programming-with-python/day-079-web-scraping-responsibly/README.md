# Day 079 lab — Scrape a Site You Are Allowed To

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Web Scraping Responsibly
- **Day number:** 79 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-079-web-scraping-responsibly
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-079-web-scraping-responsibly` when the site is running.
<!-- generated-links:end -->

## Purpose

You are going to write a web scraper. It will fetch pages over real HTTP, read
a real `robots.txt`, follow real pagination, survive real HTML mess, cache what
it fetches, and write a CSV. The one thing it will not do is touch anybody
else's server.

The site is the **Harbour Chandlery**, a three-page fake catalogue that ships
in `examples/fixtures/` and is served to you from `127.0.0.1` on a port the
operating system picks at run time. It is small, it is offline, and it is
deliberately awkward in five specific ways that real sites are awkward:

| The mess | Where | Why it is there |
| --- | --- | --- |
| a row with no price element at all | `NAV-003`, page 2 | the single most common scraping crash |
| a cell with two classes, `class="name featured"` | `NAV-002`, page 1 | defeats the obvious regular expression, not the parser |
| an HTML entity, `Ink &amp; Quill Set` | `STA-001`, page 1 | the parser decodes it; a regex hands you the raw text |
| a decorative nested tag inside a name cell | `STA-002`, page 1 | `get_text` sweeps up every descendant unless you say otherwise |
| text wrapped in newlines and indentation | `TOO-003`, page 3 | HTML authors format for humans, not for you |

And one more thing, which is the point of the day: the catalogue's first page
links to `/private/internal-notes.html`, and the site's `robots.txt` disallows
`/private/` for every client. The server will serve that page to anybody who
asks. **The test harness asserts, against the server's own access log, that
your scraper never asked.** That assertion is the difference between a lesson
about ethics and a scraper that has them.

## Learning objectives

- Fetch and parse `robots.txt` with `urllib.robotparser`, and ask it the two
  questions that matter: may I fetch this URL as this client, and how long
  must I wait between requests.
- Send an honest `User-Agent` that names your program and gives a way to reach
  you, and confirm from the server side that exactly one was sent.
- Refuse a disallowed URL **before** a socket is opened, and prove the refusal
  from the server's log rather than from your own claim.
- Extract a table with CSS selectors, and explain concretely why the obvious
  regular expression misses rows on valid HTML.
- Handle a missing element by design — `select_one` returning `None` is an
  ordinary case, not an exception.
- Follow pagination until the site says there is no next page, guard against a
  loop, and refuse a link that points at another host.
- Cache responses on disk so that a second run of your parser makes zero page
  requests, and understand why `robots.txt` is the one thing you never cache.
- Write the result to CSV with the `csv` module, putting an empty field where a
  value is missing.
- Inject the network session, the cache and the clock as parameters, so the
  suite can test a one-second crawl delay without waiting one second.

## Prerequisites

- The Day 79 lesson — read it first; the ethics half of it is the half this
  lab enforces.
- Day 78: HTTP, `requests`, `Session`, timeouts, status codes, headers.
- Day 74: testing at a boundary by injecting it rather than reaching for it.
- Days 71–73: pytest, fixtures, and reading a failing test.
- Day 65: the `csv` module, `newline=""`, and `DictReader`.
- Day 69: dataclasses and type hints.
- Day 43: creating and using a virtual environment.
- A terminal and a text editor. Nothing beyond this course is assumed.

## Supported operating systems

- **macOS** — fully supported. Executed on macOS 26.5.1 (Apple Silicon),
  Python 3.14.0, bash 3.2.57.
- **Linux** — fully supported; identical output. Everything used is either
  standard library or a pure-Python package.
- **Windows** — run inside WSL, where the commands below work unchanged.
  Outside WSL, `bash tests/run_tests.sh` needs Git Bash or WSL, and the venv
  paths become `.venv\Scripts\python` and `.venv\Scripts\pip`.

## Hardware requirements

Any machine that runs Python 3. The whole fixture site is under 20 KB, the
crawl is three pages, and the suite finishes in about a second.

## Required software

- Python 3.9 or newer (tested on 3.14.0).
- `bash` for the test harness (preinstalled on macOS and Linux).
- Three pinned packages: `beautifulsoup4==4.15.0`, `requests==2.34.2`,
  `pytest==9.1.1`. See `requirements/README.md`.

## Free and open-source options

Every tool here is free and open source, and there is no paid tier of anything
you are asked to install:

| Tool | Licence | Role |
| --- | --- | --- |
| Python + standard library | PSF | the fixture server, `robots.txt` parsing, caching, CSV |
| beautifulsoup4 | MIT | the HTML parser |
| requests | Apache 2.0 | the HTTP client |
| pytest | MIT | the test runner |

The lesson's Alternatives section also covers `lxml`, `selectolax`, Scrapy and
Playwright. All four are free and open source too; none is installed here, and
the lesson says so rather than quoting output it did not produce.

## Installation

```bash
cd labs/sections/programming-with-python/day-079-web-scraping-responsibly
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

That install is the only step that uses the internet. **The tests themselves
need no network**: the only server involved is the one this lab starts on
`127.0.0.1`.

Check it:

```bash
.venv/bin/python3 -c "import bs4, requests; print(bs4.__version__, requests.__version__)"
```

Expect `4.15.0 2.34.2`.

## File structure

```
day-079-web-scraping-responsibly/
├── README.md
├── metadata.yml
├── troubleshooting.md
├── security.md
├── requirements/
│   ├── README.md
│   └── requirements.txt
├── examples/
│   ├── fixtures/                     the fake site, served from 127.0.0.1
│   │   ├── robots.txt                disallows /private/, declares Crawl-delay: 1
│   │   ├── sitemap.txt               the machine-readable alternative to crawling
│   │   ├── index.html
│   │   ├── catalogue/page-1.html     4 items, and the disallowed link
│   │   ├── catalogue/page-2.html     4 items, one with no price element
│   │   ├── catalogue/page-3.html     4 items, the last page — no next link
│   │   ├── detour/page-1.html        a next link pointing at another host
│   │   └── private/internal-notes.html   served by the server, never requested
│   ├── fixture_server.py             local server on an ephemeral port, logs every request
│   ├── catalogue_scraper.py          the reference implementation
│   ├── regex_vs_parser.py            the same page, two ways, different answers
│   └── demo.py                       the whole thing end to end
├── starter/
│   └── catalogue_scraper.py          the same module with six exercises to write
├── tests/
│   ├── test_scraper.py               34 pytest tests
│   └── run_tests.sh                  the harness — 51 checks
└── expected-output/
    ├── FIELDS.md                     what every number means
    ├── test-run.txt                  a real harness run
    ├── sample-run.txt                a real demo run
    ├── regex-vs-parser.txt           a real comparison run
    └── catalogue.csv                 the 12-row result
```

## How to run

Read the site's rules first — as you would on a real site:

```bash
cat examples/fixtures/robots.txt
```

Check the server works on its own:

```bash
PYTHONPATH=examples .venv/bin/python3 examples/fixture_server.py
```

See why a parser beats a regular expression:

```bash
PYTHONPATH=examples .venv/bin/python3 examples/regex_vs_parser.py
```

Run the reference scraper end to end:

```bash
PYTHONPATH=examples .venv/bin/python3 examples/demo.py catalogue.csv
head -4 catalogue.csv
```

Then do the work. Open `starter/catalogue_scraper.py` and complete the six
exercises in order, running the suite against **your** module after each one:

```bash
SCRAPER_MODULE=starter .venv/bin/pytest tests -q
```

You start at `33 failed, 1 passed` and finish at `34 passed`.

Finally, the whole harness:

```bash
bash tests/run_tests.sh
```

### The six exercises

1. **Permission.** `RobotsPolicy.allows` and `RobotsPolicy.crawl_delay_seconds`
   — one line each, on top of `urllib.robotparser`. `RobotsPolicy.load` is
   already written as a worked model.
2. **Extract the table.** `parse_items` — `soup.select("table.catalogue tr.item")`
   and one `Item` per row.
3. **Survive the missing element.** `_cell_text` — `select_one`, a `None`
   check, an optional exclusion, `get_text(" ", strip=True)`.
4. **Pagination.** `next_page_url` and the `scrape_catalogue` loop — stop when
   the site says there is no next page, not after a fixed count.
5. **The cache.** `ResponseCache.get` and `.put` — a hit, a miss, and a
   human-readable `index.json`.
6. **The CSV.** `write_csv` — Day 65's rules, with an empty field where a price
   is missing.

## What the commands do

| Command | What it does |
| --- | --- |
| `cat examples/fixtures/robots.txt` | shows the site's published rules: `/private/` disallowed for everyone, `Crawl-delay: 1`, `GreedyBot` refused entirely, and a sitemap |
| `python3 examples/fixture_server.py` | starts the fixture server, fetches its own `robots.txt` once, prints the access log, and stops |
| `python3 examples/regex_vs_parser.py` | runs a naive regular expression and BeautifulSoup over the same three pages and prints both answers side by side |
| `python3 examples/demo.py catalogue.csv` | the full pipeline: parse robots, sort links by permission, crawl cold, crawl warm, write the CSV, print what the server saw |
| `SCRAPER_MODULE=starter pytest tests -q` | runs the same 34 tests against your module instead of the reference one |
| `bash tests/run_tests.sh` | the outer harness: 51 checks including the offline audit, the zero-requests assertion, and the proof that the starter's exercises are load-bearing |

## Expected output

Real captures are in `expected-output/`, and `expected-output/FIELDS.md`
explains every number. The lines worth predicting before you run anything:

```
3. First run — cold cache
   pages requested: 3 ['/catalogue/page-1.html', '/catalogue/page-2.html', '/catalogue/page-3.html']
   items found:     12
   items with no price cell: ['NAV-003'] — handled, not crashed

4. Second run — warm cache
   requests this run:      ['/robots.txt']
   page requests this run: 0 []

6. What the server saw, across every run above
   requests for /private/internal-notes.html: 0
```

And from the harness:

```
51 checks, 0 failure(s).
```

One line in `expected-output/test-run.txt` legitimately differs on your
machine — the two ephemeral port numbers. That is the check passing.

## Validation steps

1. `bash tests/run_tests.sh` exits 0 and prints `51 checks, 0 failure(s).`
2. Section 4 of that output says the disallowed path was requested **zero**
   times, per the server's own log.
3. Section 7 says a second run makes **zero** page requests.
4. `SCRAPER_MODULE=starter .venv/bin/pytest tests -q` reports `34 passed` once
   you have finished the six exercises.
5. `catalogue.csv` has 13 lines, and the `NAV-003` row's price field is empty
   rather than containing the word `None`:
   ```bash
   grep '^NAV-003' catalogue.csv
   ```
6. Nothing in `examples/`, `starter/` or `tests/` contains an absolute URL with
   a hostname in it — the harness checks this for you in section 1.

## Tests

`tests/run_tests.sh` is the outer harness and the thing to run. It performs 51
checks in nine sections:

1. **Offline by construction** — no hostname-bearing URL in the lab's source,
   the one documentation-reserved address accounted for, port 0 confirmed, and
   two servers demonstrated to get two different ports.
2. **The tools** — pytest, `bs4`, `requests` present and at the pinned
   versions.
3. **The reference suite** — `pytest tests -q` reports 34 passed.
4. **Ethics implemented, not described** — the disallowed page really is
   linked, robots.txt really does disallow it, and the server's log shows zero
   requests for it. Per-User-Agent rules are checked too.
5. **The messy realities** — all five awkward rows parse correctly.
6. **Regex versus parser** — 10 names against 12, with an undecoded entity.
7. **The cache** — zero page requests on a second run, three hits, identical
   results, no crawl delay paid on a hit.
8. **End to end** — the demo runs and its CSV is correct, including the empty
   price field and the surviving ampersand.
9. **The starter's exercises are load-bearing** — the same suite fails against
   the unfinished starter, with `NotImplementedError` rather than an import
   error.

Nothing in any of that opens a socket to any address other than `127.0.0.1`.

## Cleanup

```bash
rm -f catalogue.csv
rm -rf .venv
git checkout -- starter/    # optional: reset your work
```

The response cache lives in a temporary directory created with `mkdtemp` and
is removed when the demo ends, so there is nothing else to tidy. No process is
left running: the fixture server stops in a `finally` block.

## Troubleshooting

See `troubleshooting.md`. The three you are most likely to hit:

- `ModuleNotFoundError: No module named 'bs4'` — you install `beautifulsoup4`
  and import `bs4`. Different names, same package.
- `AttributeError: 'NoneType' object has no attribute 'get_text'` — Exercise 3,
  working as intended. `select_one` returned `None`.
- A proxy error on a loopback address — set
  `NO_PROXY=127.0.0.1` for the run.

## Security notes

See `security.md`. In short: the server binds loopback only, nothing
authenticates, nothing is sent anywhere, `robots.txt` is honoured because a
client chooses to and never because it is enforced, and everything you extract
from HTML is untrusted input until you validate it. The lab's fixture data
contains no people, deliberately.

## Extension exercises

1. **Use the sitemap instead of crawling.** `robots.txt` names
   `/sitemap.txt`. Fetch it, scrape only the pages it lists, and compare the
   result with the crawl. Then add a fourth catalogue page to the fixtures and
   see which of the two approaches finds it without a code change.
2. **Make the cache expire.** Store a timestamp beside each cached body and
   treat anything older than an hour as a miss. Then explain, in a comment,
   why you would not apply the same rule to `robots.txt`.
3. **Add a rate limiter that survives restarts.** The current crawl delay is
   per-process. Record the time of the last request in a file so that two
   consecutive runs of your program still respect one request per second
   between them.
4. **Break the site and watch your scraper fail well.** Change `td.price` to
   `td.cost` in one fixture page. Your scraper should report which page and
   which row it could not read, not silently write a CSV of empty prices. Add
   a check that fails loudly if more than half the rows are missing a field —
   that check is what tells you a site redesigned overnight.
5. **Refuse to scrape at all.** Write a small function that takes a base URL
   and returns a recommendation: use the API, use the sitemap, use the feed, or
   scrape. Feed it the fixture site and have it recommend the sitemap.
6. **Prove the negative differently.** The harness proves the disallowed path
   was never requested by reading the server's log. Add a second, independent
   proof: wrap the `requests.Session` so it records every URL it is asked for,
   and assert that list too. Two independent measurements of the same claim is
   how you catch a test that is lying to you.

## Navigation

- Previous lab: `../day-078-http-and-requests/`
- Next lab: `../day-080-building-clis-with-argparse/`
- Section index: `../README.md`
- Week 12 project: `../projects/week-12/`
