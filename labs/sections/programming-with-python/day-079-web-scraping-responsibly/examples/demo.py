"""The whole lab end to end, against the local fixture server.

Run it from the lab directory::

    PYTHONPATH=examples python3 examples/demo.py catalogue.csv

What you will see, in order:

1. robots.txt fetched and parsed, and the two questions asked of it.
2. Every link on page 1 sorted into allowed and refused — the refused one is
   never requested, and the server's own log at the end proves it.
3. A first scraping run: three pages fetched, twelve items found, one of them
   with no price at all.
4. A second run with the same cache: zero page requests. Only robots.txt is
   re-fetched, because permission is a thing you re-check, not a thing you
   cache.
5. The CSV.
6. The server's access log, which is the honest record of what we did.

Nothing here reaches the internet. The server is on 127.0.0.1 on a port the
operating system picked, and it stops when this script does.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import requests

from catalogue_scraper import (
    USER_AGENT,
    DisallowedByRobots,
    ResponseCache,
    RobotsPolicy,
    fetch_text,
    follow_links_politely,
    scrape_catalogue,
    write_csv,
)
from fixture_server import serve_fixtures


def main(argv: list[str]) -> int:
    csv_path = Path(argv[1]) if len(argv) > 1 else Path("catalogue.csv")
    cache_dir = Path(tempfile.mkdtemp(prefix="scrape-cache-"))
    recorded_sleeps: list[float] = []

    with serve_fixtures() as site, requests.Session() as session:
        print("fixture server: 127.0.0.1 on an ephemeral port")
        print(f"User-Agent:     {USER_AGENT}")
        print("note:           the crawl delay is recorded rather than slept, so this")
        print("                demo finishes instantly; a real run waits the full")
        print("                delay before every fetch that is not a cache hit.")
        print()

        # 1 -----------------------------------------------------------------
        print("1. Permission")
        robots = RobotsPolicy.load(site.base_url, session=session)
        start = site.url_for("/catalogue/page-1.html")
        private = site.url_for("/private/internal-notes.html")
        print(f"   allowed  /catalogue/page-1.html   -> {robots.allows(start)}")
        print(f"   allowed  /private/internal-notes.html -> {robots.allows(private)}")
        print(f"   crawl delay declared               -> {robots.crawl_delay_seconds()} s")
        greedy = RobotsPolicy.load(site.base_url, session=session, user_agent="GreedyBot")
        print(f"   allowed for GreedyBot              -> {greedy.allows(start)}")
        print()

        # 2 -----------------------------------------------------------------
        print("2. Links on page 1, sorted by permission")
        first_page = fetch_text(
            start,
            session=session,
            robots=robots,
            sleeper=recorded_sleeps.append,
        )
        allowed, refused = follow_links_politely(first_page, start, robots=robots)
        for url in allowed:
            print(f"   allowed: {url.removeprefix(site.base_url)}")
        for url in refused:
            print(f"   REFUSED: {url.removeprefix(site.base_url)}")
        try:
            fetch_text(private, session=session, robots=robots, sleeper=recorded_sleeps.append)
        except DisallowedByRobots as error:
            print(f"   fetching it anyway raises DisallowedByRobots on {str(error).removeprefix(site.base_url)}")
        print()

        # 3 -----------------------------------------------------------------
        print("3. First run — cold cache")
        site.reset()
        cache = ResponseCache(cache_dir)
        items = scrape_catalogue(
            start,
            session=session,
            robots=robots,
            cache=cache,
            sleeper=recorded_sleeps.append,
        )
        print(f"   pages requested: {len(site.paths())} {site.paths()}")
        print(f"   cache misses:    {cache.misses}, hits: {cache.hits}")
        print(f"   sleeps asked for: {recorded_sleeps[-3:]} (seconds, from Crawl-delay)")
        print(f"   items found:     {len(items)}")
        print()
        print("   sku      price     name")
        for item in items:
            price = " (none)" if item.price is None else f"{item.price:>7.2f}"
            print(f"   {item.sku:<8} {price}   {item.name}")
        missing = [item.sku for item in items if item.price is None]
        print(f"   items with no price cell: {missing} — handled, not crashed")
        print()

        # 4 -----------------------------------------------------------------
        print("4. Second run — warm cache")
        site.reset()
        # Permission is re-checked every run. robots.txt is the one thing we
        # deliberately do NOT cache: the site owner may have changed their mind
        # since yesterday, and a cached permission is a stale permission.
        robots_again = RobotsPolicy.load(site.base_url, session=session)
        cache2 = ResponseCache(cache_dir)
        again = scrape_catalogue(
            start,
            session=session,
            robots=robots_again,
            cache=cache2,
            sleeper=recorded_sleeps.append,
        )
        page_requests = [path for path in site.paths() if path != "/robots.txt"]
        print(f"   requests this run:      {site.paths()}")
        print(f"   page requests this run: {len(page_requests)} {page_requests}")
        print(f"   cache hits: {cache2.hits}, misses: {cache2.misses}")
        print(f"   same items as the first run: {again == items}")
        print()

        # 5 -----------------------------------------------------------------
        print("5. Output")
        write_csv(items, csv_path)
        text = csv_path.read_text(encoding="utf-8")
        print(f"   wrote {csv_path} ({len(text.splitlines())} lines including the header)")
        for line in text.splitlines()[:4]:
            print(f"   | {line}")
        print("   ...")
        for line in text.splitlines()[-1:]:
            print(f"   | {line}")
        print()

        # 6 -----------------------------------------------------------------
        print("6. What the server saw, across every run above")
        print(f"   total requests: {len(site.all_paths())}")
        print(f"   requests for /private/internal-notes.html: {site.total_count('/private/internal-notes.html')}")
        for agent in sorted(site.all_user_agents()):
            print(f"   User-Agent seen: {agent}")

    shutil.rmtree(cache_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
