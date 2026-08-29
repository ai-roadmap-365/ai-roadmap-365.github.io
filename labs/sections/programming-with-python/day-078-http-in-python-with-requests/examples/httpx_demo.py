"""The same calls in httpx — the modern alternative, if you have it.

httpx is NOT in this lab's `requirements/requirements.txt`, deliberately:
the lab's argument works with `requests` alone, and a lab should not make
you install a package to make a point about a package. If httpx happens to
be installed, this file runs and shows the differences; if it is not, it
says so and exits 0.

    python3 examples/httpx_demo.py

Two differences are worth watching for:

  * `httpx.Client` has a DEFAULT timeout of five seconds. `requests` has
    none. That single design decision is httpx's strongest argument.
  * the same code shape works with `httpx.AsyncClient` and `await`, which
    is what you want the day you need fifty model calls in flight at once.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from demo_server import base_url, running_server  # noqa: E402

try:
    import httpx
except ImportError:
    print("httpx is not installed in this environment, so this demo has nothing")
    print("to run. That is expected: httpx is not one of this lab's dependencies.")
    print("Install it with `.venv/bin/pip install httpx` if you want to compare.")
    raise SystemExit(0)


def section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def main() -> int:
    print(f"httpx {httpx.__version__}")
    with running_server() as server:
        root = base_url(server)

        section("1. The requests-shaped API, unchanged")
        with httpx.Client(headers={"User-Agent": "day078-httpx/1.0"}, timeout=10.0) as client:
            response = client.get(f"{root}/api/readings", params={"station": "ALPHA"})
            print(f"  status        : {response.status_code}")
            print(f"  path sent     : {response.request.url.raw_path.decode()}")
            print(f"  count         : {response.json()['count']}")
            print(f"  .text / .content / .json() all exist, same as requests")

            section("2. The default timeout — the difference that matters")
            default = httpx.Client()
            print(f"  httpx.Client() default timeout : {default.timeout}")
            default.close()
            print("  requests has no default timeout at all. A missing timeout=")
            print("  in requests hangs; in httpx it gives up after 5 seconds.")

            section("3. raise_for_status, and a 404")
            missing = client.get(f"{root}/api/missing")
            print(f"  status        : {missing.status_code}")
            print(f"  is_success    : {missing.is_success}")
            try:
                missing.raise_for_status()
            except httpx.HTTPStatusError as exc:
                print(f"  raised        : {type(exc).__name__}")

            section("4. Streaming")
            total = 0
            chunks = 0
            with client.stream("GET", f"{root}/api/large?kb=256") as stream:
                for chunk in stream.iter_bytes(8192):
                    total += len(chunk)
                    chunks += 1
            print(f"  bytes         : {total} in {chunks} chunk(s)")

            section("5. What httpx adds")
            print("  * a default timeout;")
            print("  * the same API in sync and async (httpx.AsyncClient);")
            print("  * HTTP/2 support, if you install the extra: pip install 'httpx[http2]'")
            print("    and pass http2=True. Without that extra it speaks HTTP/1.1,")
            print("    exactly like requests.")
            print("  * a strict URL and header model, which catches some mistakes")
            print("    requests would let through.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
