#!/usr/bin/env bash
# Tests for the Day 079 lab. Run from the lab directory:
#   bash tests/run_tests.sh
#
# NOTHING HERE TOUCHES THE INTERNET. Section 1 proves that rather than
# asserting it: the only absolute URLs in the lab's source point at 127.0.0.1
# or at 198.51.100.0/24, the range the IETF reserves for documentation, and
# the one reference to that range exists precisely so a test can watch the
# scraper REFUSE to connect to it. Everything else is served by a local
# fixture server on a port the operating system picks at run time.
#
# The check worth reading is in section 4. The fixture site links a page that
# robots.txt disallows, and the server will serve it to anyone who asks. The
# harness asserts, against the SERVER's own access log, that the path was
# never requested. A scraper that only describes good behaviour cannot pass
# that check — which is the difference between ethics implemented and ethics
# described.
#
# Non-interactive, deterministic, exits 0 only if every check passes.
set -u

export PYTHONDONTWRITEBYTECODE=1

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
checks=0

check() {
  local label="$1" ok="$2"
  checks=$((checks + 1))
  if [ "${ok}" = "yes" ]; then
    echo "  ok: ${label}"
  else
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

# Resolve tools: an explicit override, then this lab's .venv, then PATH.
# Fails loudly with instructions rather than silently skipping.
resolve_tool() {
  local tool="$1" override="$2"
  if [ -n "${override}" ] && [ -x "${override}" ]; then echo "${override}"; return 0; fi
  if [ -x "${lab_dir}/.venv/bin/${tool}" ]; then echo "${lab_dir}/.venv/bin/${tool}"; return 0; fi
  if command -v "${tool}" >/dev/null 2>&1; then command -v "${tool}"; return 0; fi
  return 1
}

pytest_bin="$(resolve_tool pytest "${PYTEST:-}")" || {
  echo "FAIL: pytest not found." >&2
  echo "  Install this lab's dependencies with:" >&2
  echo "    python3 -m venv .venv" >&2
  echo "    .venv/bin/pip install -r requirements/requirements.txt" >&2
  echo "  Or point this suite at an existing pytest: PYTEST=/path/to/pytest bash tests/run_tests.sh" >&2
  exit 1
}

python_bin="$(resolve_tool python3 "${PYTHON:-}")" || {
  echo "FAIL: python3 not found on PATH." >&2
  exit 1
}
if [ -x "${lab_dir}/.venv/bin/python3" ]; then
  python_bin="${lab_dir}/.venv/bin/python3"
fi

echo "Day 079 — Scrape a Site You Are Allowed To"
echo

# --------------------------------------------------------------------------
echo "1. Offline by construction"
# --------------------------------------------------------------------------

# Any absolute http(s) URL beginning with a letter would be a hostname, which
# would mean a DNS lookup. There must be none in the lab's own source.
if grep -rEn 'https?://[A-Za-z]' \
     "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/tests" >/dev/null 2>&1; then
  check "no hostname-bearing URL anywhere in examples/, starter/ or tests/" "no"
  grep -rEn 'https?://[A-Za-z]' "${lab_dir}/examples" "${lab_dir}/starter" "${lab_dir}/tests"
else
  check "no hostname-bearing URL anywhere in examples/, starter/ or tests/" "yes"
fi

# The one absolute URL with a foreign host is the documentation-reserved
# address in the detour fixture, and it exists to be refused.
detour_hits="$(grep -Ec '198\.51\.100\.' "${lab_dir}/examples/fixtures/detour/page-1.html" || true)"
if [ "${detour_hits}" = "1" ]; then
  check "the only off-site link is a documentation-reserved address (198.51.100.0/24)" "yes"
else
  check "the only off-site link is a documentation-reserved address (got ${detour_hits} occurrences)" "no"
fi

# The server binds port 0, not a fixed port, so it never collides.
if grep -q '("127.0.0.1", 0)' "${lab_dir}/examples/fixture_server.py"; then
  check "the fixture server binds port 0 and reads back the assigned port" "yes"
else
  check "the fixture server binds port 0 and reads back the assigned port" "no"
fi

# Two servers started in a row must land on different ports — that is what
# "ephemeral" means, and it is why the lab cannot clash with your own work.
ports="$(cd "${lab_dir}" && PYTHONPATH=examples "${python_bin}" - <<'PY'
from fixture_server import serve_fixtures
with serve_fixtures() as a, serve_fixtures() as b:
    print(a.port, b.port, a.port != b.port)
PY
)"
case "${ports}" in
  *True) check "two fixture servers get two different ephemeral ports ( ${ports% True} )" "yes" ;;
  *) check "two fixture servers get two different ephemeral ports (got '${ports}')" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "2. The tools"
# --------------------------------------------------------------------------

version_line="$("${pytest_bin}" --version 2>&1 | head -1)"
case "${version_line}" in
  pytest*) check "pytest --version reports a pytest ( ${version_line} )" "yes" ;;
  *) check "pytest --version reports a pytest ( ${version_line} )" "no" ;;
esac

bs4_version="$("${python_bin}" -c 'import bs4; print(bs4.__version__)' 2>&1)"
case "${bs4_version}" in
  4.*) check "beautifulsoup4 imports as bs4 ( ${bs4_version} )" "yes" ;;
  *) check "beautifulsoup4 imports as bs4 (got: ${bs4_version})" "no" ;;
esac

requests_version="$("${python_bin}" -c 'import requests; print(requests.__version__)' 2>&1)"
case "${requests_version}" in
  2.*) check "requests is importable ( ${requests_version} )" "yes" ;;
  *) check "requests is importable (got: ${requests_version})" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "3. The reference suite"
# --------------------------------------------------------------------------

suite_out="$(cd "${lab_dir}" && "${pytest_bin}" tests -q 2>&1)"
suite_exit=$?
if [ "${suite_exit}" -eq 0 ]; then
  check "pytest tests exits 0 against examples/" "yes"
else
  check "pytest tests exits 0 against examples/ (got ${suite_exit})" "no"
  echo "${suite_out}" | tail -30
fi

case "${suite_out}" in
  *"34 passed"*) check "the reference suite reports 34 passed" "yes" ;;
  *) check "the reference suite reports 34 passed (got: $(printf '%s' "${suite_out}" | tail -1))" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "4. Ethics implemented, not described"
# --------------------------------------------------------------------------

# The private page IS linked from page 1 and the server WILL serve it. The
# only reason it is never fetched is that the scraper asks robots.txt first.
if grep -q '/private/internal-notes.html' "${lab_dir}/examples/fixtures/catalogue/page-1.html"; then
  check "the fixture really does link the disallowed page from page 1" "yes"
else
  check "the fixture really does link the disallowed page from page 1" "no"
fi

if grep -q 'Disallow: /private/' "${lab_dir}/examples/fixtures/robots.txt"; then
  check "robots.txt really does disallow /private/ for every User-Agent" "yes"
else
  check "robots.txt really does disallow /private/ for every User-Agent" "no"
fi

# Independent evidence: ask the server, not the scraper.
private_report="$(cd "${lab_dir}" && PYTHONPATH=examples "${python_bin}" - <<'PY'
import tempfile
from pathlib import Path

import requests

from catalogue_scraper import ResponseCache, RobotsPolicy, scrape_catalogue
from fixture_server import serve_fixtures

with serve_fixtures() as site, requests.Session() as session:
    robots = RobotsPolicy.load(site.base_url, session=session)
    cache = ResponseCache(Path(tempfile.mkdtemp(prefix="d079-")))
    items = scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=cache,
        sleeper=lambda seconds: None,
    )
    print("private_requests", site.total_count("/private/internal-notes.html"))
    print("items", len(items))
    print("pages", len([p for p in site.paths() if p.startswith("/catalogue/")]))
    print("agents", len(site.all_user_agents()))
PY
)"
case "${private_report}" in
  *"private_requests 0"*) check "the disallowed path was requested ZERO times, per the server's own log" "yes" ;;
  *) check "the disallowed path was requested ZERO times (report: ${private_report})" "no" ;;
esac
case "${private_report}" in
  *"pages 3"*) check "pagination followed all 3 pages and stopped" "yes" ;;
  *) check "pagination followed all 3 pages and stopped" "no" ;;
esac
case "${private_report}" in
  *"items 12"*) check "the crawl found all 12 items" "yes" ;;
  *) check "the crawl found all 12 items" "no" ;;
esac
case "${private_report}" in
  *"agents 1"*) check "exactly one User-Agent string was sent — the client identified itself" "yes" ;;
  *) check "exactly one User-Agent string was sent" "no" ;;
esac

# The named-agent rules in robots.txt are honoured too.
greedy="$(cd "${lab_dir}" && PYTHONPATH=examples "${python_bin}" - <<'PY'
import requests
from catalogue_scraper import RobotsPolicy
from fixture_server import serve_fixtures

with serve_fixtures() as site, requests.Session() as session:
    polite = RobotsPolicy.load(site.base_url, session=session)
    greedy = RobotsPolicy.load(site.base_url, session=session, user_agent="GreedyBot")
    target = site.url_for("/catalogue/page-1.html")
    print("polite", polite.allows(target), "greedy", greedy.allows(target),
          "delay", polite.crawl_delay_seconds())
PY
)"
case "${greedy}" in
  "polite True greedy False delay 1.0") check "robots.txt rules are per-User-Agent ( ${greedy} )" "yes" ;;
  *) check "robots.txt rules are per-User-Agent (got: ${greedy})" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "5. The messy realities"
# --------------------------------------------------------------------------

messy="$(cd "${lab_dir}" && PYTHONPATH=examples "${python_bin}" - <<'PY'
from pathlib import Path
from catalogue_scraper import parse_items

base = Path("examples/fixtures/catalogue")
one = parse_items(base.joinpath("page-1.html").read_text(encoding="utf-8"))
two = parse_items(base.joinpath("page-2.html").read_text(encoding="utf-8"))
three = parse_items(base.joinpath("page-3.html").read_text(encoding="utf-8"))
by_sku = {item.sku: item for item in one + two + three}
print("missing_price", by_sku["NAV-003"].price, "rows_on_page_2", len(two))
print("entity", repr(by_sku["STA-001"].name))
print("nested", repr(by_sku["STA-002"].name))
print("second_class", repr(by_sku["NAV-002"].name))
print("whitespace", repr(by_sku["TOO-003"].name))
PY
)"
case "${messy}" in
  *"missing_price None rows_on_page_2 4"*)
    check "the item with no price cell yields price=None and does not shorten the page" "yes" ;;
  *) check "the item with no price cell yields price=None (got: ${messy})" "no" ;;
esac
case "${messy}" in
  *"entity 'Ink & Quill Set'"*) check "the HTML entity &amp; is decoded to '&'" "yes" ;;
  *) check "the HTML entity &amp; is decoded to '&'" "no" ;;
esac
case "${messy}" in
  *"nested 'Vellum Notebook'"*) check "the decorative nested tag is kept out of the name" "yes" ;;
  *) check "the decorative nested tag is kept out of the name" "no" ;;
esac
case "${messy}" in
  *"second_class 'Mariner Astrolabe'"*) check "a cell with two classes is still found by td.name" "yes" ;;
  *) check "a cell with two classes is still found by td.name" "no" ;;
esac
case "${messy}" in
  *"whitespace 'Linen Thread Spool'"*) check "whitespace-wrapped text is stripped" "yes" ;;
  *) check "whitespace-wrapped text is stripped" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "6. The regular expression fails where the parser does not"
# --------------------------------------------------------------------------

regex_out="$(cd "${lab_dir}" && PYTHONPATH=examples "${python_bin}" examples/regex_vs_parser.py 2>&1)"
regex_exit=$?
if [ "${regex_exit}" -eq 0 ]; then
  check "examples/regex_vs_parser.py exits 0" "yes"
else
  check "examples/regex_vs_parser.py exits 0 (got ${regex_exit})" "no"
fi
case "${regex_out}" in
  *"regular expression found: 10 names"*) check "the naive regex finds only 10 of the 12 names" "yes" ;;
  *) check "the naive regex finds only 10 of the 12 names" "no" ;;
esac
case "${regex_out}" in
  *"BeautifulSoup found: 12 names"*) check "the parser finds all 12" "yes" ;;
  *) check "the parser finds all 12" "no" ;;
esac
case "${regex_out}" in
  *"'Ink &amp; Quill Set'"*) check "the regex hands back an undecoded HTML entity" "yes" ;;
  *) check "the regex hands back an undecoded HTML entity" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "7. The cache means a re-run costs the site nothing"
# --------------------------------------------------------------------------

cache_report="$(cd "${lab_dir}" && PYTHONPATH=examples "${python_bin}" - <<'PY'
import shutil, tempfile
from pathlib import Path

import requests

from catalogue_scraper import ResponseCache, RobotsPolicy, scrape_catalogue
from fixture_server import serve_fixtures

cache_dir = Path(tempfile.mkdtemp(prefix="d079-cache-"))
with serve_fixtures() as site, requests.Session() as session:
    robots = RobotsPolicy.load(site.base_url, session=session)
    start = site.url_for("/catalogue/page-1.html")
    first = scrape_catalogue(start, session=session, robots=robots,
                             cache=ResponseCache(cache_dir), sleeper=lambda s: None)
    site.reset()
    waits = []
    warm = ResponseCache(cache_dir)
    second = scrape_catalogue(start, session=session, robots=robots,
                              cache=warm, sleeper=waits.append)
    pages = [p for p in site.paths() if p != "/robots.txt"]
    print("second_run_page_requests", len(pages))
    print("hits", warm.hits, "misses", warm.misses)
    print("identical", first == second)
    print("sleeps_on_cache_hits", len(waits))
    print("cache_files", len(list(cache_dir.glob("*.html"))))
shutil.rmtree(cache_dir, ignore_errors=True)
PY
)"
case "${cache_report}" in
  *"second_run_page_requests 0"*) check "a second run makes ZERO page requests" "yes" ;;
  *) check "a second run makes ZERO page requests (report: ${cache_report})" "no" ;;
esac
case "${cache_report}" in
  *"hits 3 misses 0"*) check "all three pages came from the cache" "yes" ;;
  *) check "all three pages came from the cache" "no" ;;
esac
case "${cache_report}" in
  *"identical True"*) check "the cached run produces byte-identical items" "yes" ;;
  *) check "the cached run produces byte-identical items" "no" ;;
esac
case "${cache_report}" in
  *"sleeps_on_cache_hits 0"*) check "a cache hit does not pay the crawl delay" "yes" ;;
  *) check "a cache hit does not pay the crawl delay" "no" ;;
esac
case "${cache_report}" in
  *"cache_files 3"*) check "the cache holds one file per page fetched" "yes" ;;
  *) check "the cache holds one file per page fetched" "no" ;;
esac

# --------------------------------------------------------------------------
echo
echo "8. End to end: the demo and its CSV"
# --------------------------------------------------------------------------

work="$(mktemp -d "${TMPDIR:-/tmp}/d079-demo.XXXXXX")"
demo_out="$(cd "${lab_dir}" && PYTHONPATH=examples "${python_bin}" examples/demo.py "${work}/catalogue.csv" 2>&1)"
demo_exit=$?
if [ "${demo_exit}" -eq 0 ]; then
  check "examples/demo.py exits 0" "yes"
else
  check "examples/demo.py exits 0 (got ${demo_exit})" "no"
  echo "${demo_out}" | tail -20
fi
case "${demo_out}" in
  *"requests for /private/internal-notes.html: 0"*)
    check "the demo's closing server log shows zero requests for the disallowed path" "yes" ;;
  *) check "the demo's closing server log shows zero requests for the disallowed path" "no" ;;
esac
case "${demo_out}" in
  *"page requests this run: 0"*) check "the demo's second run makes no page requests" "yes" ;;
  *) check "the demo's second run makes no page requests" "no" ;;
esac

if [ -f "${work}/catalogue.csv" ]; then
  csv_lines="$(wc -l < "${work}/catalogue.csv" | tr -d ' ')"
  if [ "${csv_lines}" = "13" ]; then
    check "the CSV has 13 lines: a header and 12 items" "yes"
  else
    check "the CSV has 13 lines (got ${csv_lines})" "no"
  fi
  # The csv module's default dialect ends lines with CRLF, as RFC 4180 asks.
  # That is correct, and it is also why this comparison strips the carriage
  # return rather than pretending the byte is not there.
  header="$(head -1 "${work}/catalogue.csv" | tr -d '\r')"
  if [ "${header}" = "sku,name,price,stock,source_path" ]; then
    check "the CSV header names the five columns" "yes"
  else
    check "the CSV header names the five columns (got '${header}')" "no"
  fi
  if head -1 "${work}/catalogue.csv" | grep -q $'\r'; then
    check "the CSV uses RFC 4180 CRLF line endings, as the csv module defaults to" "yes"
  else
    check "the CSV uses RFC 4180 CRLF line endings" "no"
  fi
  if grep -q '^NAV-003,Brass Compass,,4,' "${work}/catalogue.csv"; then
    check "the price-less item writes an EMPTY field, not the word None" "yes"
  else
    check "the price-less item writes an EMPTY field, not the word None" "no"
  fi
  if grep -q 'Ink & Quill Set' "${work}/catalogue.csv"; then
    check "the ampersand survives HTML, parsing and CSV" "yes"
  else
    check "the ampersand survives HTML, parsing and CSV" "no"
  fi
  if grep -q 'None' "${work}/catalogue.csv"; then
    check "the CSV contains no literal 'None'" "no"
  else
    check "the CSV contains no literal 'None'" "yes"
  fi
else
  check "examples/demo.py wrote the CSV" "no"
fi
rm -rf "${work}"

# --------------------------------------------------------------------------
echo
echo "9. The starter's exercises are load-bearing"
# --------------------------------------------------------------------------

starter_out="$(cd "${lab_dir}" && SCRAPER_MODULE=starter "${pytest_bin}" tests -q 2>&1)"
starter_exit=$?
if [ "${starter_exit}" -ne 0 ]; then
  check "the same suite FAILS against the unfinished starter (exit ${starter_exit})" "yes"
else
  check "the same suite FAILS against the unfinished starter — it did not, so the exercises are vacuous" "no"
fi
case "${starter_out}" in
  *"NotImplementedError"*) check "the starter fails on its own NotImplementedError, not on an import error" "yes" ;;
  *) check "the starter fails on its own NotImplementedError, not on an import error" "no" ;;
esac
case "${starter_out}" in
  *"1 passed"*) check "exactly one test passes on the starter — the worked RobotsPolicy.load" "yes" ;;
  *) check "exactly one test passes on the starter ( $(printf '%s' "${starter_out}" | tail -1) )" "no" ;;
esac

for exercise in "Exercise 1a" "Exercise 1b" "Exercise 2" "Exercise 3" "Exercise 4a" "Exercise 4b" "Exercise 5a" "Exercise 5b" "Exercise 6"; do
  if grep -q "${exercise}" "${lab_dir}/starter/catalogue_scraper.py"; then
    check "the starter names ${exercise}" "yes"
  else
    check "the starter names ${exercise}" "no"
  fi
done

echo
echo "${checks} checks, ${failures} failure(s)."
[ "${failures}" -eq 0 ]
