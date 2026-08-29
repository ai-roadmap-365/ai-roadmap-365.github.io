# Dependencies — Day 079 lab

Three packages, all free and open source, all pinned to the exact version this
lab was executed against.

| Pin | Why this lab needs it | Licence | Cost |
| --- | --- | --- | --- |
| `beautifulsoup4==4.15.0` | the HTML parser. Imported as `bs4`, not `beautifulsoup4` — the distribution name and the import name differ, which trips up nearly everyone once. | MIT | free |
| `requests==2.34.2` | the HTTP client from Day 78, used here with a `Session`, a timeout and an explicit `User-Agent` header. | Apache 2.0 | free |
| `pytest==9.1.1` | the test runner from Week 11. | MIT | free |

Everything else is standard library and needs no install:

| Module | Used for |
| --- | --- |
| `urllib.robotparser` | reading and applying `robots.txt` — the whole ethics half of this lab runs on a module that ships with Python |
| `urllib.parse` | `urljoin` for relative links, `urlparse` for the host guard |
| `http.server`, `socketserver`, `threading` | the local fixture server that stands in for a real site |
| `hashlib`, `json`, `pathlib` | the on-disk response cache |
| `csv` | the output, per Day 65 |
| `dataclasses`, `typing` | the `Item` type, per Day 69 |

Note what is **not** here. There is no `lxml`, no `selectolax`, no `scrapy`
and no `playwright`. The lesson's Alternatives section covers all four
honestly, and none of them is installed on this machine, so the lesson
describes them without quoting output it did not produce. `beautifulsoup4`
with the standard library's `html.parser` backend needs no compiler, works
everywhere Python works, and is the right default for a job this size.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

`.venv/` is already ignored by the repository. The test runner finds
`.venv/bin/pytest` on its own; you never need to activate anything.

## The one thing that needs the network

Installing those three packages downloads them from the Python Package Index,
which needs an internet connection **once**. After that, **the tests need no
network at all** — that is the entire design of this lab. The fixture server
runs on 127.0.0.1, on a port the operating system assigns, serving HTML files
that ship in `examples/fixtures/`. If you are on a plane, and the packages are
already installed, everything here still passes.

## Verify your setup

```bash
.venv/bin/python3 -c "import bs4, requests; print(bs4.__version__, requests.__version__)"
```

That should print `4.15.0 2.34.2`. If `import bs4` fails with
`ModuleNotFoundError` after a successful `pip install beautifulsoup4`, you
have almost certainly installed into a different interpreter than the one you
are running — see `troubleshooting.md`.

## Windows

Run everything inside WSL, where the commands above work unchanged. Outside
WSL the paths become `.venv\Scripts\pip` and `.venv\Scripts\python`, and
`bash tests/run_tests.sh` needs Git Bash or WSL because the harness is a bash
script.
