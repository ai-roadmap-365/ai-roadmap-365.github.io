"""Day 079 starter — a polite, cached, parser-based scraper.

Six numbered exercises. Everything else in this file is finished and working,
including ``RobotsPolicy.load``, which is left complete on purpose so you have
a worked model of the style the rest of the file expects.

Work in order. After each exercise, run the suite against YOUR module:

    SCRAPER_MODULE=starter .venv/bin/pytest tests -q

The number of failures should fall each time. When it reaches zero, run the
whole harness:

    bash tests/run_tests.sh

The reference answer is in ``examples/catalogue_scraper.py``. Read it after
you have made each exercise pass, not before — the exercises are short, and
the value is entirely in the attempt.

Every boundary here is a parameter, not a global: the ``session``, the
``cache``, the ``sleeper``. That is Day 74's rule. Keep it that way, or the
tests will have to wait real seconds and you will stop running them.
"""

from __future__ import annotations

import csv
import hashlib
import json
import time
import urllib.robotparser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Identify yourself honestly, and leave a way to be contacted. `example.com`
# is reserved by the IETF for documentation, so this address belongs to
# nobody; put a real one in a real scraper.
USER_AGENT = "HarbourCatalogueLab/1.0 (course exercise; contact: scraper-owner@example.com)"

DEFAULT_TIMEOUT = 10.0
FALLBACK_DELAY_SECONDS = 1.0


class ScrapeError(Exception):
    """Base class for everything this module refuses to do."""


class DisallowedByRobots(ScrapeError):
    """The path is disallowed by robots.txt for our User-Agent."""


class OffSite(ScrapeError):
    """The URL points somewhere other than the site we were asked to scrape."""


# ===========================================================================
# EXERCISE 1 — permission, before anything else
# ===========================================================================
#
# `RobotsPolicy.load` below is written for you. Implement the two questions
# the rest of the program asks of it.
#
# `allows`: return True when `self.parser.can_fetch(self.user_agent, url)` says
#   so. One line. Note that can_fetch takes the User-Agent string, because
#   robots.txt can carry different rules for different clients — the fixture
#   robots.txt refuses "GreedyBot" everything, and a test checks that.
#
# `crawl_delay_seconds`: ask `self.parser.crawl_delay(self.user_agent)`. It
#   returns None when the site declares no delay; in that case return
#   `default`. Return a float either way.
#
# Tests: test_robots_allows_the_catalogue_and_refuses_the_private_path,
#        test_a_named_user_agent_gets_its_own_rules,
#        test_the_declared_crawl_delay_is_read_from_robots_txt,
#        test_a_missing_crawl_delay_falls_back_to_a_polite_default
# ===========================================================================


@dataclass
class RobotsPolicy:
    """A parsed robots.txt, and the two questions worth asking it."""

    parser: urllib.robotparser.RobotFileParser
    user_agent: str

    @classmethod
    def load(
        cls,
        base_url: str,
        *,
        session: requests.Session,
        user_agent: str = USER_AGENT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> "RobotsPolicy":
        """WORKED EXAMPLE — read this, then write the two methods below."""
        robots_url = urljoin(base_url, "/robots.txt")
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_url)
        response = session.get(
            robots_url, headers={"User-Agent": user_agent}, timeout=timeout
        )
        if response.status_code == 200:
            parser.parse(response.text.splitlines())
        elif response.status_code in (401, 403):
            parser.disallow_all = True
        else:
            parser.allow_all = True
        return cls(parser=parser, user_agent=user_agent)

    def allows(self, url: str) -> bool:
        """Is this exact URL allowed for our User-Agent?"""
        raise NotImplementedError(
            "Exercise 1a: return self.parser.can_fetch(self.user_agent, url)"
        )

    def crawl_delay_seconds(self, default: float = FALLBACK_DELAY_SECONDS) -> float:
        """Seconds to wait between requests, per robots.txt, else ``default``."""
        raise NotImplementedError(
            "Exercise 1b: ask self.parser.crawl_delay(self.user_agent); "
            "return float(it) unless it is None, in which case return default"
        )


# ===========================================================================
# EXERCISE 5 — the response cache
# ===========================================================================
#
# `get`: build the path with `self._path_for(url)`. If it exists, increment
#   `self.hits` and return its text (encoding="utf-8"). Otherwise increment
#   `self.misses` and return None. Returning None rather than raising is what
#   lets `fetch_text` treat "not cached" as an ordinary case.
#
# `put`: write the text to `self._path_for(url)`, then add the filename-to-URL
#   pair to `index.json` in the same directory so the cache is readable by a
#   human. Load the existing index if the file is there.
#
# Tests: test_a_second_run_makes_no_page_requests,
#        test_a_cache_hit_does_not_pay_the_crawl_delay,
#        test_the_cache_directory_is_inspectable
# ===========================================================================


@dataclass
class ResponseCache:
    """Response bodies stored on disk, keyed by URL."""

    directory: Path
    hits: int = 0
    misses: int = 0

    def __post_init__(self) -> None:
        self.directory = Path(self.directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path_for(self, url: str) -> Path:
        """WORKED — a stable filename per URL, safe on every filesystem."""
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
        return self.directory / f"{digest}.html"

    def get(self, url: str) -> str | None:
        raise NotImplementedError(
            "Exercise 5a: return the cached text and count a hit, or None and "
            "count a miss"
        )

    def put(self, url: str, text: str) -> None:
        raise NotImplementedError(
            "Exercise 5b: write the body to self._path_for(url), then record "
            "{filename: url} in index.json alongside it"
        )


# ===========================================================================
# fetch_text — WORKED. Read the ORDER of the four steps; it is the lesson.
# ===========================================================================


def fetch_text(
    url: str,
    *,
    session: requests.Session,
    robots: RobotsPolicy,
    cache: ResponseCache | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    delay_seconds: float | None = None,
    user_agent: str = USER_AGENT,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Return the body of ``url``, from cache if possible, politely if not."""
    # 1. Permission, before a socket is opened.
    if not robots.allows(url):
        raise DisallowedByRobots(url)

    # 2. Cache, so a page is fetched once in its life.
    if cache is not None:
        cached = cache.get(url)
        if cached is not None:
            return cached

    # 3. The crawl delay, paid only by a real fetch.
    wait = robots.crawl_delay_seconds() if delay_seconds is None else delay_seconds
    if wait > 0:
        sleeper(wait)

    # 4. The request itself, with a timeout (Day 78) and an honest User-Agent.
    response = session.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
    response.raise_for_status()
    text = response.text
    if cache is not None:
        cache.put(url, text)
    return text


@dataclass(frozen=True)
class Item:
    """One catalogue row. ``price`` is ``None`` when the page omits the cell."""

    sku: str
    name: str
    price: float | None
    stock: int | None
    source_path: str


# ===========================================================================
# EXERCISE 3 — survive the missing element
# ===========================================================================
#
# This is the four-line function that decides whether your scraper crashes at
# 3 a.m. on row 4,812. Write it before Exercise 2 uses it.
#
#   cell = row.select_one(selector)      # returns None, never raises
#   if cell is None: return None         # the caller decides what that means
#   for extra in cell.select(drop): extra.extract()   # only when drop is given
#   return cell.get_text(" ", strip=True)
#
# Two things `get_text(" ", strip=True)` does for you: it strips the
# whitespace HTML authors leave around text, and it joins nested text with a
# space instead of gluing words together. `drop` exists because get_text
# sweeps up EVERY descendant, including a decorative <span class="badge">.
#
# Tests: test_the_item_with_no_price_cell_parses_instead_of_crashing,
#        test_a_row_with_no_cells_at_all_still_parses,
#        test_whitespace_wrapped_text_is_stripped,
#        test_a_decorative_nested_tag_is_kept_out_of_the_name
# ===========================================================================


def _cell_text(row, selector: str, *, drop: str | None = None) -> str | None:
    """Text of the first cell matching ``selector``, or ``None`` if absent."""
    raise NotImplementedError(
        "Exercise 3: select_one, check for None, optionally extract() the "
        "elements matching `drop`, then get_text(' ', strip=True)"
    )


# ===========================================================================
# EXERCISE 2 — extract the table with CSS selectors
# ===========================================================================
#
#   soup = BeautifulSoup(html, "html.parser")
#   for row in soup.select("table.catalogue tr.item"):
#       sku        = row.get("data-sku", "")
#       name       = _cell_text(row, "td.name", drop="span.badge") or ""
#       price_text = _cell_text(row, "td.price")
#       stock_text = _cell_text(row, "td.stock")
#       ... build an Item, converting price to float and stock to int, but
#           leaving each as None when its text is missing or empty ...
#
# Why `tr.item` and `td.name` rather than a regular expression: a CSS class
# selector matches a class that is PRESENT in the attribute, so it still finds
# `class="name featured"`. The obvious regex for `class="name"` does not, and
# it will not tell you that it missed anything.
#
# Tests: test_the_first_page_yields_four_items_in_document_order,
#        test_a_second_class_on_the_cell_does_not_hide_it,
#        test_an_html_entity_is_decoded_not_returned_raw,
#        test_prices_and_stock_are_numbers_not_strings
# ===========================================================================


def parse_items(html: str, *, source_path: str = "") -> list[Item]:
    """Extract every catalogue row from one page."""
    raise NotImplementedError(
        "Exercise 2: BeautifulSoup(html, 'html.parser').select("
        "'table.catalogue tr.item') and build one Item per row"
    )


# ===========================================================================
# EXERCISE 4 — pagination, to the end and no further
# ===========================================================================
#
# `next_page_url`: find `nav.pager a.next` with select_one. If there is no
#   such link — the last page has a <span class="next disabled"> instead —
#   return None. Otherwise return `urljoin(current_url, link.get("href"))`, so
#   the relative "page-2.html" becomes an absolute URL.
#
# `scrape_catalogue`: loop from `start_url`. On each turn, refuse a URL whose
#   netloc differs from the start URL's (raise OffSite), stop if you have seen
#   this URL before or have hit `max_pages`, fetch it with `fetch_text`,
#   extend the item list with `parse_items(html, source_path=urlparse(url).path)`,
#   and move on to `next_page_url(html, url)`.
#
# Do NOT stop after a fixed number of pages or when the item count reaches
# twelve. Pages get added. Stop when the site says there is no next page.
#
# Tests: test_next_page_url_is_resolved_against_the_current_url,
#        test_the_last_page_reports_no_next_page,
#        test_pagination_visits_every_page_exactly_once,
#        test_the_crawl_finds_every_item_across_all_pages,
#        test_an_off_site_link_is_refused_rather_than_followed
# ===========================================================================


def next_page_url(html: str, current_url: str) -> str | None:
    """Absolute URL of the next page, or ``None`` when this was the last one."""
    raise NotImplementedError(
        "Exercise 4a: select_one('nav.pager a.next'); None when absent; "
        "otherwise urljoin(current_url, href)"
    )


def scrape_catalogue(
    start_url: str,
    *,
    session: requests.Session,
    robots: RobotsPolicy,
    cache: ResponseCache | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    delay_seconds: float | None = None,
    max_pages: int = 50,
) -> list[Item]:
    """Follow the pagination from ``start_url`` and return every item found."""
    raise NotImplementedError(
        "Exercise 4b: the while loop — guard the host, guard against repeats "
        "and max_pages, fetch, parse, then follow next_page_url"
    )


def follow_links_politely(
    html: str,
    base_url: str,
    *,
    robots: RobotsPolicy,
) -> tuple[list[str], list[str]]:
    """WORKED — split every link on a page into (allowed, refused)."""
    soup = BeautifulSoup(html, "html.parser")
    allowed: list[str] = []
    refused: list[str] = []
    for anchor in soup.select("a[href]"):
        target = urljoin(base_url, anchor["href"])
        (allowed if robots.allows(target) else refused).append(target)
    return allowed, refused


# ===========================================================================
# EXERCISE 6 — write the CSV (Day 65)
# ===========================================================================
#
#   open the path with encoding="utf-8" and newline="" — the csv module
#   requires newline="", and forgetting it gives you blank lines on Windows
#   write CSV_COLUMNS as the header row
#   one row per item: sku, name, price formatted to two decimals, stock,
#   source_path — and an EMPTY STRING, not the word "None", where a value is
#   missing. A CSV containing the string None is a CSV that will be loaded as
#   text by whatever reads it next.
#
# Tests: test_the_csv_has_a_header_and_one_row_per_item,
#        test_the_missing_price_becomes_an_empty_field_not_the_word_none,
#        test_the_ampersand_survives_the_round_trip
# ===========================================================================

CSV_COLUMNS: Sequence[str] = ("sku", "name", "price", "stock", "source_path")


def write_csv(items: Iterable[Item], path: Path) -> Path:
    """Write items to ``path`` as CSV and return the path."""
    raise NotImplementedError(
        "Exercise 6: csv.writer into an open(..., newline='', encoding='utf-8'), "
        "header first, empty string for a missing price or stock"
    )
