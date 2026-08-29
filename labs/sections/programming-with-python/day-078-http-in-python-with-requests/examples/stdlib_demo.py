"""The same four calls, without installing anything.

`requests` is not on the machine of every person who will run your script.
`urllib.request` and `http.client` are, because they ship with Python. This
file makes the three-way comparison concrete by doing the same work with
each of them against the same local test server.

Run it:

    python3 examples/stdlib_demo.py

Nothing here imports `requests`, and nothing here leaves 127.0.0.1.
"""

from __future__ import annotations

import http.client
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from demo_server import base_url, running_server  # noqa: E402


def section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def main() -> int:
    with running_server() as server:
        root = base_url(server)
        host, port = server.server_address[:2]

        section("1. urllib.request — a GET with a query string")
        query = urllib.parse.urlencode({"station": "ALPHA"})
        url = f"{root}/api/readings?{query}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "day078-urllib/1.0", "Accept": "application/json"},
        )
        # A timeout is a parameter here too, and it is just as optional and
        # just as necessary. Note what you have to do by hand: build the
        # query string, set the headers, decode the bytes, parse the JSON.
        with urllib.request.urlopen(req, timeout=10.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
        print(f"  status      : {response.status} {response.reason}")
        print(f"  content type: {response.headers['Content-Type']}")
        print(f"  count       : {payload['count']}")
        print(f"  first row   : {payload['readings'][0]}")
        print("  note        : you encoded the query, decoded the bytes, and")
        print("                parsed the JSON yourself. requests does all three.")

        section("2. urllib.request — a 404 is an EXCEPTION, not a status")
        try:
            with urllib.request.urlopen(f"{root}/api/missing", timeout=10.0):
                print("  unreachable")
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read().decode("utf-8"))
            print(f"  raised      : {type(exc).__name__}")
            print(f"  status      : {exc.code}")
            print(f"  detail      : {body['detail']}")
            print("  note        : this is the big behavioural difference. urllib")
            print("                raises on 4xx and 5xx; requests returns a")
            print("                response and lets you decide.")

        section("3. urllib.request — a POST with a JSON body")
        data = json.dumps({"station": "ALPHA", "note": "hand rolled"}).encode("utf-8")
        req = urllib.request.Request(
            f"{root}/api/echo",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "day078-urllib/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=10.0) as response:
            echoed = json.loads(response.read().decode("utf-8"))
        print(f"  status      : {response.status}")
        print(f"  server saw  : method={echoed['method']} bytes={echoed['body_bytes']}")
        print(f"  server saw  : content_type={echoed['content_type']}")
        print(f"  echoed json : {echoed['json']}")

        section("4. http.client — the layer underneath both")
        before = server.connections
        conn = http.client.HTTPConnection(host, port, timeout=10.0)
        try:
            conn.request(
                "GET",
                "/api/readings?station=BRAVO",
                headers={"Accept": "application/json", "User-Agent": "day078-httpclient/1.0"},
            )
            response = conn.getresponse()
            raw = response.read()
            print(f"  status      : {response.status} {response.reason}")
            print(f"  headers     : {len(response.getheaders())} of them")
            print(f"  body bytes  : {len(raw)}")
            print(f"  count       : {json.loads(raw.decode('utf-8'))['count']}")
            # The same connection, used twice. This is what a Session does
            # for you automatically; here it is manual.
            conn.request("GET", "/control/stats", headers={"Accept": "application/json"})
            conn.getresponse().read()
            print(f"  connections : {server.connections - before} opened for those 2 requests")
            print("  note        : http.client speaks the protocol and nothing")
            print("                more — no redirects, no pooling, no decoding.")
        finally:
            conn.close()

        section("5. What each layer costs you")
        print("  http.client     : the protocol, exactly. You manage everything.")
        print("  urllib.request  : redirects and a bit of convenience; verbose,")
        print("                    and it raises on 4xx/5xx.")
        print("  requests        : params=, .json(), Session pooling, retries via")
        print("                    an adapter, streaming. One pip install away.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
