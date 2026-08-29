"""The reference suite for Day 079.

It runs against ``examples/catalogue_scraper.py`` by default and against
``starter/catalogue_scraper.py`` when ``SCRAPER_MODULE=starter`` is set. The
starter run is expected to FAIL until the six exercises are finished — that is
how ``tests/run_tests.sh`` proves the exercises are load-bearing rather than
decorative.

Every test in this file is offline. The only socket opened points at
127.0.0.1, at a port the operating system chose, serving files that ship with
this lab. Nothing resolves a hostname and nothing leaves the machine.

The check that matters most is ``test_the_disallowed_path_is_never_requested``.
It does not ask the scraper what it did; it asks the *server* what it was
asked for. A scraper that describes good behaviour in a docstring cannot pass
it.
"""

from __future__ import annotations

import importlib
import os
import re
import sys
from pathlib import Path

import pytest
import requests

LAB_DIR = Path(__file__).resolve().parent.parent
WHICH = os.environ.get("SCRAPER_MODULE", "examples")
sys.path.insert(0, str(LAB_DIR / "examples"))
sys.path.insert(0, str(LAB_DIR / WHICH))

scraper = importlib.import_module("catalogue_scraper")
from fixture_server import serve_fixtures  # noqa: E402

EXPECTED_ITEM_COUNT = 12
EXPECTED_PAGES = [
    "/catalogue/page-1.html",
    "/catalogue/page-2.html",
    "/catalogue/page-3.html",
]
PRIVATE_PATH = "/private/internal-notes.html"


class RecordingSleeper:
    """A stand-in for ``time.sleep`` that records instead of waiting.

    Day 74's boundary rule, applied to the clock: the scraper takes a
    ``sleeper`` parameter, so the suite can assert that it asked to wait one
    second between fetches without the suite taking three seconds to run.
    """

    def __init__(self) -> None:
        self.waits: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.waits.append(seconds)


@pytest.fixture
def site():
    with serve_fixtures() as server:
        yield server


@pytest.fixture
def session():
    with requests.Session() as s:
        yield s


@pytest.fixture
def robots(site, session):
    return scraper.RobotsPolicy.load(site.base_url, session=session)


# ---------------------------------------------------------------------------
# Exercise 1 — robots.txt is consulted before anything is fetched
# ---------------------------------------------------------------------------


def test_robots_txt_is_fetched_with_our_own_user_agent(site, session):
    scraper.RobotsPolicy.load(site.base_url, session=session)
    assert site.paths() == ["/robots.txt"]
    assert site.user_agents() == {scraper.USER_AGENT}


def test_robots_allows_the_catalogue_and_refuses_the_private_path(site, robots):
    assert robots.allows(site.url_for("/catalogue/page-1.html")) is True
    assert robots.allows(site.url_for(PRIVATE_PATH)) is False


def test_a_named_user_agent_gets_its_own_rules(site, session):
    greedy = scraper.RobotsPolicy.load(
        site.base_url, session=session, user_agent="GreedyBot"
    )
    assert greedy.allows(site.url_for("/catalogue/page-1.html")) is False


def test_the_declared_crawl_delay_is_read_from_robots_txt(robots):
    assert robots.crawl_delay_seconds() == 1.0


def test_a_missing_crawl_delay_falls_back_to_a_polite_default(site, session, tmp_path):
    bare = tmp_path / "site"
    (bare / "catalogue").mkdir(parents=True)
    (bare / "robots.txt").write_text("User-agent: *\nDisallow: /nowhere/\n")
    with serve_fixtures(bare) as plain_site:
        policy = scraper.RobotsPolicy.load(plain_site.base_url, session=session)
        assert policy.crawl_delay_seconds() == pytest.approx(1.0)
        assert policy.crawl_delay_seconds(default=2.5) == pytest.approx(2.5)


def test_fetching_a_disallowed_url_raises_before_any_request(site, session, robots):
    site.reset()
    with pytest.raises(scraper.DisallowedByRobots):
        scraper.fetch_text(
            site.url_for(PRIVATE_PATH),
            session=session,
            robots=robots,
            sleeper=RecordingSleeper(),
        )
    assert site.paths() == []


def test_the_disallowed_path_is_never_requested(site, session, robots, tmp_path):
    """The check that proves the ethics were implemented, not described.

    The private page is linked from page 1, the server will happily serve it,
    and the crawl walks right past it. The assertion reads the SERVER's log.
    """
    site.reset()
    cache = scraper.ResponseCache(tmp_path / "cache")
    scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=cache,
        sleeper=RecordingSleeper(),
    )
    first_page = (LAB_DIR / "examples/fixtures/catalogue/page-1.html").read_text()
    assert PRIVATE_PATH in first_page, "the fixture must actually link the private page"
    assert site.count(PRIVATE_PATH) == 0
    assert site.total_count(PRIVATE_PATH) == 0


def test_links_are_sorted_into_allowed_and_refused(site, session, robots):
    start = site.url_for("/catalogue/page-1.html")
    html = scraper.fetch_text(
        start, session=session, robots=robots, sleeper=RecordingSleeper()
    )
    allowed, refused = scraper.follow_links_politely(html, start, robots=robots)
    assert refused == [site.url_for(PRIVATE_PATH)]
    assert site.url_for("/catalogue/page-2.html") in allowed


def test_the_site_publishes_a_sitemap_that_beats_guessing(site, session, robots):
    """The alternatives-first rule, in miniature.

    robots.txt names a sitemap. Reading it gives you every page directly,
    with no pagination logic to get wrong and no pages missed when the site
    adds a fourth one. Look for this before you write a crawl loop.
    """
    sitemap_url = site.url_for("/sitemap.txt")
    body = scraper.fetch_text(
        sitemap_url, session=session, robots=robots, sleeper=RecordingSleeper()
    )
    listed = [line.strip() for line in body.splitlines() if line.strip()]
    assert listed == EXPECTED_PAGES


# ---------------------------------------------------------------------------
# Exercise 2 — CSS selectors extract the table
# ---------------------------------------------------------------------------


def page_html(name: str) -> str:
    return (LAB_DIR / "examples/fixtures/catalogue" / name).read_text(encoding="utf-8")


def test_the_first_page_yields_four_items_in_document_order():
    items = scraper.parse_items(page_html("page-1.html"), source_path="/p1")
    assert [item.sku for item in items] == ["NAV-001", "NAV-002", "STA-001", "STA-002"]


def test_a_second_class_on_the_cell_does_not_hide_it():
    items = scraper.parse_items(page_html("page-1.html"))
    astrolabe = next(item for item in items if item.sku == "NAV-002")
    assert astrolabe.name == "Mariner Astrolabe"
    assert astrolabe.price == pytest.approx(128.50)


def test_an_html_entity_is_decoded_not_returned_raw():
    items = scraper.parse_items(page_html("page-1.html"))
    quills = next(item for item in items if item.sku == "STA-001")
    assert quills.name == "Ink & Quill Set"
    assert "&amp;" not in quills.name


def test_a_decorative_nested_tag_is_kept_out_of_the_name():
    items = scraper.parse_items(page_html("page-1.html"))
    notebook = next(item for item in items if item.sku == "STA-002")
    assert notebook.name == "Vellum Notebook"


def test_whitespace_wrapped_text_is_stripped():
    items = scraper.parse_items(page_html("page-3.html"))
    thread = next(item for item in items if item.sku == "TOO-003")
    assert thread.name == "Linen Thread Spool"


def test_prices_and_stock_are_numbers_not_strings():
    items = scraper.parse_items(page_html("page-1.html"))
    sextant = items[0]
    assert isinstance(sextant.price, float)
    assert isinstance(sextant.stock, int)
    assert sextant.price == pytest.approx(42.00)
    assert sextant.stock == 7


# ---------------------------------------------------------------------------
# Exercise 3 — survive the missing element
# ---------------------------------------------------------------------------


def test_the_item_with_no_price_cell_parses_instead_of_crashing():
    items = scraper.parse_items(page_html("page-2.html"), source_path="/p2")
    compass = next(item for item in items if item.sku == "NAV-003")
    assert compass.name == "Brass Compass"
    assert compass.price is None
    assert compass.stock == 4


def test_the_missing_price_does_not_shorten_the_page():
    items = scraper.parse_items(page_html("page-2.html"))
    assert len(items) == 4


def test_a_row_with_no_cells_at_all_still_parses():
    html = '<table class="catalogue"><tr class="item" data-sku="X-1"></tr></table>'
    items = scraper.parse_items(html)
    assert len(items) == 1
    assert items[0].sku == "X-1"
    assert items[0].name == ""
    assert items[0].price is None


# ---------------------------------------------------------------------------
# Exercise 4 — pagination to the end
# ---------------------------------------------------------------------------


def test_next_page_url_is_resolved_against_the_current_url(site):
    current = site.url_for("/catalogue/page-1.html")
    assert scraper.next_page_url(page_html("page-1.html"), current) == site.url_for(
        "/catalogue/page-2.html"
    )


def test_the_last_page_reports_no_next_page(site):
    current = site.url_for("/catalogue/page-3.html")
    assert scraper.next_page_url(page_html("page-3.html"), current) is None


def test_pagination_visits_every_page_exactly_once(site, session, robots, tmp_path):
    site.reset()
    scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(tmp_path / "cache"),
        sleeper=RecordingSleeper(),
    )
    assert site.paths() == EXPECTED_PAGES


def test_the_crawl_finds_every_item_across_all_pages(site, session, robots, tmp_path):
    items = scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(tmp_path / "cache"),
        sleeper=RecordingSleeper(),
    )
    assert len(items) == EXPECTED_ITEM_COUNT
    assert len({item.sku for item in items}) == EXPECTED_ITEM_COUNT
    assert sum(1 for item in items if item.price is None) == 1


def test_the_crawl_waits_the_declared_delay_before_each_real_fetch(
    site, session, robots, tmp_path
):
    sleeper = RecordingSleeper()
    scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(tmp_path / "cache"),
        sleeper=sleeper,
    )
    assert sleeper.waits == [1.0, 1.0, 1.0]


def test_an_off_site_link_is_refused_rather_than_followed(site, session, robots):
    """The detour fixture's Next link points at a host reserved for docs.

    It must be refused before any connection is attempted — the assertion on
    the server log shows the crawl stopped after the one page it was allowed.
    """
    site.reset()
    with pytest.raises(scraper.OffSite):
        scraper.scrape_catalogue(
            site.url_for("/detour/page-1.html"),
            session=session,
            robots=robots,
            sleeper=RecordingSleeper(),
        )
    assert site.paths() == ["/detour/page-1.html"]


# ---------------------------------------------------------------------------
# Exercise 5 — the cache
# ---------------------------------------------------------------------------


def test_a_second_run_makes_no_page_requests(site, session, robots, tmp_path):
    cache_dir = tmp_path / "cache"
    start = site.url_for("/catalogue/page-1.html")
    first = scraper.scrape_catalogue(
        start,
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(cache_dir),
        sleeper=RecordingSleeper(),
    )
    site.reset()
    warm = scraper.ResponseCache(cache_dir)
    second = scraper.scrape_catalogue(
        start, session=session, robots=robots, cache=warm, sleeper=RecordingSleeper()
    )
    assert site.paths() == []
    assert warm.hits == 3
    assert warm.misses == 0
    assert second == first


def test_a_cache_hit_does_not_pay_the_crawl_delay(site, session, robots, tmp_path):
    cache_dir = tmp_path / "cache"
    start = site.url_for("/catalogue/page-1.html")
    scraper.scrape_catalogue(
        start,
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(cache_dir),
        sleeper=RecordingSleeper(),
    )
    sleeper = RecordingSleeper()
    scraper.scrape_catalogue(
        start,
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(cache_dir),
        sleeper=sleeper,
    )
    assert sleeper.waits == []


def test_the_cache_directory_is_inspectable(site, session, robots, tmp_path):
    cache_dir = tmp_path / "cache"
    scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(cache_dir),
        sleeper=RecordingSleeper(),
    )
    index = cache_dir / "index.json"
    assert index.exists()
    import json

    mapping = json.loads(index.read_text(encoding="utf-8"))
    assert sorted(mapping.values()) == [site.url_for(path) for path in EXPECTED_PAGES]


def test_scraping_without_a_cache_still_works(site, session, robots):
    site.reset()
    items = scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=None,
        sleeper=RecordingSleeper(),
    )
    assert len(items) == EXPECTED_ITEM_COUNT
    assert site.paths() == EXPECTED_PAGES


# ---------------------------------------------------------------------------
# Exercise 6 — CSV output
# ---------------------------------------------------------------------------


def test_the_csv_has_a_header_and_one_row_per_item(site, session, robots, tmp_path):
    items = scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(tmp_path / "cache"),
        sleeper=RecordingSleeper(),
    )
    out = scraper.write_csv(items, tmp_path / "catalogue.csv")
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "sku,name,price,stock,source_path"
    assert len(lines) == EXPECTED_ITEM_COUNT + 1


def test_the_missing_price_becomes_an_empty_field_not_the_word_none(
    site, session, robots, tmp_path
):
    items = scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(tmp_path / "cache"),
        sleeper=RecordingSleeper(),
    )
    out = scraper.write_csv(items, tmp_path / "catalogue.csv")
    import csv as csv_module

    with out.open(newline="", encoding="utf-8") as handle:
        rows = list(csv_module.DictReader(handle))
    compass = next(row for row in rows if row["sku"] == "NAV-003")
    assert compass["price"] == ""
    assert "None" not in out.read_text(encoding="utf-8")


def test_the_ampersand_survives_the_round_trip(site, session, robots, tmp_path):
    items = scraper.scrape_catalogue(
        site.url_for("/catalogue/page-1.html"),
        session=session,
        robots=robots,
        cache=scraper.ResponseCache(tmp_path / "cache"),
        sleeper=RecordingSleeper(),
    )
    out = scraper.write_csv(items, tmp_path / "catalogue.csv")
    import csv as csv_module

    with out.open(newline="", encoding="utf-8") as handle:
        rows = list(csv_module.DictReader(handle))
    quills = next(row for row in rows if row["sku"] == "STA-001")
    assert quills["name"] == "Ink & Quill Set"


# ---------------------------------------------------------------------------
# The parser earns its place: a regular expression cannot do this
# ---------------------------------------------------------------------------

NAIVE_NAME_RE = re.compile(r'<td class="name">([^<]*)</td>')


def test_the_naive_regex_misses_rows_the_parser_finds():
    html = page_html("page-1.html")
    regex_names = [match.group(1) for match in NAIVE_NAME_RE.finditer(html)]
    parser_names = [item.name for item in scraper.parse_items(html)]
    assert len(parser_names) == 4
    assert len(regex_names) == 2
    assert "Mariner Astrolabe" in parser_names
    assert "Mariner Astrolabe" not in regex_names


def test_the_naive_regex_returns_an_undecoded_entity():
    html = page_html("page-1.html")
    regex_names = [match.group(1) for match in NAIVE_NAME_RE.finditer(html)]
    assert "Ink &amp; Quill Set" in regex_names
    parser_names = [item.name for item in scraper.parse_items(html)]
    assert "Ink & Quill Set" in parser_names
    assert "Ink &amp; Quill Set" not in parser_names


def test_the_naive_regex_returns_unstripped_whitespace():
    html = page_html("page-3.html")
    regex_names = [match.group(1) for match in NAIVE_NAME_RE.finditer(html)]
    assert any(name != name.strip() for name in regex_names)
    parser_names = [item.name for item in scraper.parse_items(html)]
    assert all(name == name.strip() for name in parser_names)
