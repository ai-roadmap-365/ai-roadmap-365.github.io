"""A local fixture web server that counts every request it receives.

Nothing in this lab talks to the internet. Instead we serve the fake catalogue
in ``examples/fixtures/`` over real HTTP from 127.0.0.1, so the scraper you
write is a real scraper making real requests — it just cannot reach anyone
else's machine.

Two details make this useful rather than merely offline:

* The port is **ephemeral**. We bind port 0 and read back whatever the
  operating system assigned. Hard-coding 8000 collides with whatever the
  learner already has running, and a lab that fails because of a port clash
  teaches nothing.
* Every request is **recorded**. ``FixtureServer.requests`` is the server's own
  log, not the client's. That is what lets the test suite prove a negative:
  the path robots.txt disallows was never even asked for. A scraper that
  merely *says* it honours robots.txt cannot fake this.

Standard library only: ``http.server``, ``socketserver``, ``threading``.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@dataclass
class RequestRecord:
    """One line of the server's access log."""

    method: str
    path: str
    user_agent: str


@dataclass
class FixtureServer:
    """A running server plus the log of everything it was asked for."""

    host: str
    port: int
    requests: list[RequestRecord] = field(default_factory=list)
    history: list[RequestRecord] = field(default_factory=list)

    @property
    def base_url(self) -> str:
        """The root URL of this run, e.g. ``http://127.0.0.1:54321``."""
        return f"http://{self.host}:{self.port}"

    def url_for(self, path: str) -> str:
        """Absolute URL for a site-root-relative path such as ``/robots.txt``."""
        return self.base_url + path

    def paths(self) -> list[str]:
        """Every path requested, in order."""
        return [record.path for record in self.requests]

    def count(self, path: str) -> int:
        """How many times ``path`` was requested. The ethics assertion uses this."""
        return self.paths().count(path)

    def user_agents(self) -> set[str]:
        """The distinct User-Agent strings seen. An honest client sends one."""
        return {record.user_agent for record in self.requests}

    def all_paths(self) -> list[str]:
        """Every path requested since the server started, across all resets."""
        return [record.path for record in self.history] + self.paths()

    def total_count(self, path: str) -> int:
        """Requests for ``path`` since the server started, ignoring resets."""
        return self.all_paths().count(path)

    def all_user_agents(self) -> set[str]:
        """Distinct User-Agent strings seen since the server started."""
        return {record.user_agent for record in self.history} | self.user_agents()

    def reset(self) -> None:
        """Start a fresh log so the next run can be measured on its own.

        The old records move to ``history`` rather than being destroyed, so a
        question like "was the disallowed path *ever* requested?" still has an
        answer at the end of the program.
        """
        self.history.extend(self.requests)
        self.requests.clear()


def _make_handler(record_to: list[RequestRecord], directory: Path):
    class RecordingHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def _record(self, method: str) -> None:
            record_to.append(
                RequestRecord(
                    method=method,
                    path=self.path,
                    user_agent=self.headers.get("User-Agent", ""),
                )
            )

        def do_GET(self) -> None:  # noqa: N802 - name fixed by http.server
            self._record("GET")
            super().do_GET()

        def do_HEAD(self) -> None:  # noqa: N802 - name fixed by http.server
            self._record("HEAD")
            super().do_HEAD()

        def log_message(self, fmt: str, *args) -> None:
            """Silence the default stderr access log; we keep our own."""

    return RecordingHandler


@contextmanager
def serve_fixtures(directory: Path | None = None) -> Iterator[FixtureServer]:
    """Serve ``directory`` on 127.0.0.1 and an ephemeral port for the block.

    Usage::

        with serve_fixtures() as site:
            html = requests.get(site.url_for("/catalogue/page-1.html")).text
            assert site.count("/private/internal-notes.html") == 0

    The server is shut down and joined on the way out, including when the body
    raises, so a failing test never leaves a stray listener behind.
    """
    directory = directory or FIXTURES
    records: list[RequestRecord] = []
    handler = _make_handler(records, directory)

    # Port 0 means "any free port"; server_address tells us which one we got.
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    host, port = httpd.server_address[0], httpd.server_address[1]

    # A short poll interval keeps shutdown() quick; the default of 0.5 seconds
    # would add half a second to the teardown of every test that starts a
    # server, which is the difference between a suite people run and one they
    # skip.
    thread = threading.Thread(
        target=httpd.serve_forever, kwargs={"poll_interval": 0.02}, name="fixture-server"
    )
    thread.daemon = True
    thread.start()
    try:
        yield FixtureServer(host=host, port=port, requests=records)
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":  # A quick manual check of the server itself.
    import urllib.request

    with serve_fixtures() as site:
        with urllib.request.urlopen(site.url_for("/robots.txt")) as response:
            first_line = response.read().decode().splitlines()[0]
        print("served from 127.0.0.1 on an ephemeral port")
        print("first line of robots.txt:", first_line)
        print("requests recorded:", site.paths())
