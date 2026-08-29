"""Why a parser beats a regular expression, demonstrated on valid HTML.

Run it::

    python3 examples/regex_vs_parser.py

No server and no network: this reads the three fixture pages straight off the
disk. The regular expression below is not a straw man. It is exactly what a
careful person writes on their first attempt, it is anchored on the real
markup, and it works perfectly on the first row of the first page — which is
the trap. Every failure it produces here comes from HTML that is completely
valid and that a browser renders without complaint.
"""

from __future__ import annotations

import re
from pathlib import Path

from catalogue_scraper import parse_items

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "catalogue"
PAGES = ["page-1.html", "page-2.html", "page-3.html"]

# The obvious regular expression: find a name cell, capture what is inside it.
NAME_RE = re.compile(r'<td class="name">([^<]*)</td>')


def regex_names(html: str) -> list[str]:
    return [match.group(1) for match in NAME_RE.finditer(html)]


def main() -> None:
    regex_found: list[str] = []
    parser_found: list[str] = []

    for page in PAGES:
        html = (FIXTURES / page).read_text(encoding="utf-8")
        regex_found.extend(regex_names(html))
        parser_found.extend(item.name for item in parse_items(html, source_path=page))

    print("regular expression found:", len(regex_found), "names")
    for name in regex_found:
        print(f"  {name!r}")

    print()
    print("BeautifulSoup found:", len(parser_found), "names")
    for name in parser_found:
        print(f"  {name!r}")

    missed = [name for name in parser_found if name not in regex_found]
    print()
    print("missed by the regular expression:", len(missed))
    for name in missed:
        print(f"  {name!r}")

    print()
    print("Three different failures, all on valid HTML:")
    print("  1. class=\"name featured\" — a second class defeats the literal match")
    print("  2. a nested <span> inside the cell — [^<]* stops at the '<'")
    print("  3. &amp; is returned raw; the parser decodes it to '&'")


if __name__ == "__main__":
    main()
