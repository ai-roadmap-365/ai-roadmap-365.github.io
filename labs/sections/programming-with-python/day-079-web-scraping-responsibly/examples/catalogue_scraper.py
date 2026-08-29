"""A polite, cached, parser-based scraper for the fixture catalogue.

This is the reference implementation. ``starter/catalogue_scraper.py`` is the
same file with six numbered exercises hollowed out; the same test suite runs
against both, which is how you know the exercises are load-bearing.

The shape of the module is the lesson in code, in this order:

1. ``RobotsPolicy``  — permission, decided BEFORE any page is fetched.
2. ``ResponseCache`` — a page fetched once is never fetched again.
3. ``fetch_text``    — the only function that is allowed to make a request.
4. ``parse_items``   — pure: HTML in, ``Item`` objects out, no network.
5. ``next_page_url`` — pure: finds the pagination link, or ``None`` at the end.
6. ``scrape_catalogue`` / ``write_csv`` — the loop and the output.

Every boundary — the network session, the clock, the cache directory — is a
parameter rather than a global. That is Day 74's rule, and it is the reason
the tests can run this scraper with a fake clock and count the sleeps it asked
for without ever waiting a real second.
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

# Identify yourself honestly, and leave a way to be contacted. A site owner
# who can see who you are and reach you will usually ask you to slow down
# before they block you. `example.com` is reserved by the IETF for
# documentation, so this address belongs to nobody; put a real one in a real
# scraper.
USER_AGENT = "HarbourCatalogueLab/1.0 (course exercise; contact: scraper-owner@example.com)"

DEFAULT_TIMEOUT = 10.0
FALLBACK_DELAY_SECONDS = 1.0


class ScrapeError(Exception):
    """Base class for everything this module refuses to do."""


class DisallowedByRobots(ScrapeError):
    """The path is disallowed by robots.txt for our User-Agent."""


class OffSite(ScrapeError):
    """The URL points somewhere other than the site we were asked to scrape."""


# ---------------------------------------------------------------------------
# 1. Permission
# ---------------------------------------------------------------------------


@dataclass
class RobotsPolicy:
    """A parsed robots.txt, and the two questions worth asking it.

    Built with :meth:`load` so that the fetch of robots.txt itself goes through
    our own session with our own User-Agent. ``RobotFileParser.read()`` would
    also work, but it opens its own connection with urllib's default header,
    which means the site cannot tell it was us.
    """

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
        robots_url = urljoin(base_url, "/robots.txt")
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_url)
        response = session.get(
            robots_url, headers={"User-Agent": user_agent}, timeout=timeout
        )
        if response.status_code == 200:
            parser.parse(response.text.splitlines())
        elif response.status_code in (401, 403):
            # RFC 9309: an authentication or forbidden status means the whole
            # site is off limits. Treat it that way rather than shrugging.
            parser.disallow_all = True
        else:
            # 404 and other 4xx mean "no rules published", which permits all.
            parser.allow_all = True
        return cls(parser=parser, user_agent=user_agent)

    def allows(self, url: str) -> bool:
        """Is this exact URL allowed for our User-Agent?"""
        return self.parser.can_fetch(self.user_agent, url)

    def crawl_delay_seconds(self, default: float = FALLBACK_DELAY_SECONDS) -> float:
        """Seconds to wait between requests, per robots.txt, else ``default``.

        Note that ``RobotFileParser`` only accepts whole-number crawl delays;
        a fractional value in robots.txt is ignored and you get ``None`` here.
        """
        declared = self.parser.crawl_delay(self.user_agent)
        return float(declared) if declared is not None else default


# ---------------------------------------------------------------------------
# 2. The cache
# ---------------------------------------------------------------------------


@dataclass
class ResponseCache:
    """Response bodies stored on disk, keyed by URL.

    The point is not speed, though it is faster. The point is that while you
    are getting the parser right — and you will iterate on the parser twenty
    times — the site is asked for each page exactly once. Re-running your
    program should cost the person who owns that server nothing.
    """

    directory: Path
    hits: int = 0
    misses: int = 0

    def __post_init__(self) -> None:
        self.directory = Path(self.directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path_for(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
        return self.directory / f"{digest}.html"

    def get(self, url: str) -> str | None:
        path = self._path_for(url)
        if path.exists():
            self.hits += 1
            return path.read_text(encoding="utf-8")
        self.misses += 1
        return None

    def put(self, url: str, text: str) -> None:
        self._path_for(url).write_text(text, encoding="utf-8")
        # A human-readable map, so a cache directory is inspectable rather
        # than being 32 hex characters of mystery.
        index_path = self.directory / "index.json"
        index: dict[str, str] = {}
        if index_path.exists():
            index = json.loads(index_path.read_text(encoding="utf-8"))
        index[self._path_for(url).name] = url
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# 3. The only function allowed to make a request
# ---------------------------------------------------------------------------


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
    """Return the body of ``url``, from cache if possible, politely if not.

    Raises :class:`DisallowedByRobots` before any socket is opened if the path
    is refused. The order matters: check, then cache, then sleep, then fetch.
    """
    if not robots.allows(url):
        raise DisallowedByRobots(url)

    if cache is not None:
        cached = cache.get(url)
        if cached is not None:
            return cached

    # Only a real fetch pays the crawl delay. A cache hit costs the site
    # nothing, so waiting for it would be politeness theatre.
    wait = robots.crawl_delay_seconds() if delay_seconds is None else delay_seconds
    if wait > 0:
        sleeper(wait)

    response = session.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
    response.raise_for_status()
    text = response.text
    if cache is not None:
        cache.put(url, text)
    return text


# ---------------------------------------------------------------------------
# 4. Parsing — pure functions, no network
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Item:
    """One catalogue row. ``price`` is ``None`` when the page omits the cell."""

    sku: str
    name: str
    price: float | None
    stock: int | None
    source_path: str


def _cell_text(row, selector: str, *, drop: str | None = None) -> str | None:
    """Text of the first cell matching ``selector``, or ``None`` if absent.

    Three habits live in these few lines and all three matter more than they
    look.

    ``select_one`` returns ``None`` rather than raising, so the caller decides
    what a missing cell means — this is the single most common scraping bug,
    and the fix is to never chain ``.text`` onto a lookup you have not checked.

    ``get_text(" ", strip=True)`` collapses the whitespace that HTML authors
    put around text for readability, and BeautifulSoup has already turned
    ``&amp;`` back into ``&`` by this point.

    ``drop`` removes elements you do not want swept up. ``get_text`` returns
    the text of *every* descendant, so a decorative ``<span class="badge">new</span>``
    inside a name cell silently becomes part of the product name unless you
    say otherwise. Naming your exclusions is cheaper than explaining later why
    forty rows are called "Something new".
    """
    cell = row.select_one(selector)
    if cell is None:
        return None
    if drop:
        for extra in cell.select(drop):
            extra.extract()
    return cell.get_text(" ", strip=True)


def parse_items(html: str, *, source_path: str = "") -> list[Item]:
    """Extract every catalogue row from one page.

    ``tr.item`` matches rows whose class *contains* ``item``, which is why the
    ``class="name featured"`` cell below is found by ``td.name`` while the
    obvious regular expression for ``class="name"`` misses it entirely.
    """
    soup = BeautifulSoup(html, "html.parser")
    items: list[Item] = []
    for row in soup.select("table.catalogue tr.item"):
        sku = row.get("data-sku", "")
        name = _cell_text(row, "td.name", drop="span.badge") or ""
        price_text = _cell_text(row, "td.price")
        stock_text = _cell_text(row, "td.stock")
        items.append(
            Item(
                sku=sku,
                name=name,
                price=float(price_text) if price_text else None,
                stock=int(stock_text) if stock_text else None,
                source_path=source_path,
            )
        )
    return items


def next_page_url(html: str, current_url: str) -> str | None:
    """Absolute URL of the next page, or ``None`` when this was the last one.

    The last page carries ``<span class="next disabled">`` instead of a link,
    so ``a.next`` finds nothing and the loop stops. Do not stop on an item
    count or a page number — pages get added.
    """
    soup = BeautifulSoup(html, "html.parser")
    link = soup.select_one("nav.pager a.next")
    if link is None:
        return None
    href = link.get("href")
    if not href:
        return None
    return urljoin(current_url, href)


# ---------------------------------------------------------------------------
# 5. The loop
# ---------------------------------------------------------------------------


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
    """Follow the pagination from ``start_url`` and return every item found.

    ``max_pages`` and the ``seen`` set are not decoration. A pagination loop
    that points back at itself is common enough that an unbounded crawler will
    eventually hammer somebody's server until they block you.
    """
    items: list[Item] = []
    seen: set[str] = set()
    url: str | None = start_url
    origin = urlparse(start_url)

    while url is not None and len(seen) < max_pages:
        if url in seen:
            break
        if urlparse(url).netloc != origin.netloc:
            raise OffSite(url)
        seen.add(url)
        html = fetch_text(
            url,
            session=session,
            robots=robots,
            cache=cache,
            sleeper=sleeper,
            delay_seconds=delay_seconds,
        )
        items.extend(parse_items(html, source_path=urlparse(url).path))
        url = next_page_url(html, url)

    return items


def follow_links_politely(
    html: str,
    base_url: str,
    *,
    robots: RobotsPolicy,
) -> tuple[list[str], list[str]]:
    """Split every link on a page into (allowed, refused) by robots.txt.

    This is the function the harness uses to prove the ethics were implemented
    rather than described: the disallowed link is present in the HTML, it is
    discovered, and it is put in the refused list instead of being requested.
    """
    soup = BeautifulSoup(html, "html.parser")
    allowed: list[str] = []
    refused: list[str] = []
    for anchor in soup.select("a[href]"):
        target = urljoin(base_url, anchor["href"])
        (allowed if robots.allows(target) else refused).append(target)
    return allowed, refused


# ---------------------------------------------------------------------------
# 6. Output
# ---------------------------------------------------------------------------

CSV_COLUMNS: Sequence[str] = ("sku", "name", "price", "stock", "source_path")


def write_csv(items: Iterable[Item], path: Path) -> Path:
    """Write items to ``path`` as CSV, using Day 65's rules.

    ``newline=""`` is required by the csv module, a missing price becomes an
    empty field rather than the string ``None``, and the file is UTF-8 so the
    ampersand-and-friends survive.
    """
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_COLUMNS)
        for item in items:
            writer.writerow(
                [
                    item.sku,
                    item.name,
                    "" if item.price is None else f"{item.price:.2f}",
                    "" if item.stock is None else item.stock,
                    item.source_path,
                ]
            )
    return path
