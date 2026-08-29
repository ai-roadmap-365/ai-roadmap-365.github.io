"""HTTP with no HTTP library at all — just a socket and some text.

This is the demystifying one. `requests` is a convenience; underneath it,
an HTTP request is a few lines of ASCII sent down a TCP connection, and an
HTTP response is a few lines of ASCII sent back. You can type it by hand,
and here we do.

Run it:

    python3 examples/raw_socket_demo.py

Everything it prints was really sent and really received over a loopback
connection to the local test server started by this script.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from demo_server import running_server  # noqa: E402


def show(label: str, raw: bytes) -> None:
    print(f"  {label} ({len(raw)} bytes)")
    print("  " + "-" * (len(label) + 12))
    text = raw.decode("utf-8", errors="replace")
    lines = text.split("\r\n")
    while lines and lines[-1] == "":
        lines.pop()
    for line in lines:
        print(f"    {line}\\r\\n")
    print("    \\r\\n          <- the blank line: headers finished")
    print()


def main() -> int:
    with running_server() as server:
        host, port = server.server_address[:2]

        print("1. The request, typed out by hand")
        print("=================================")
        print("  Four parts: a request line, some headers, a blank line, and")
        print("  (for a GET) no body. Every line ends with carriage return +")
        print("  line feed, and the blank line is what says 'headers finished'.")
        print()

        request = (
            "GET /api/readings?station=ALPHA HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "User-Agent: day078-raw-socket/1.0\r\n"
            "Accept: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("ascii")
        show("bytes sent", request)

        with socket.create_connection((host, port), timeout=5.0) as sock:
            sock.sendall(request)
            received = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                received += chunk

        print("2. The response, exactly as it arrived")
        print("======================================")
        print("  Three parts: a status line, some headers, a blank line, then")
        print("  the body. The body here is JSON, but HTTP neither knows nor")
        print("  cares — Content-Type is what says so.")
        print()

        head, _, body = received.partition(b"\r\n\r\n")
        show("status line and headers", head + b"\r\n")
        print(f"  body ({len(body)} bytes)")
        print("  " + "-" * 18)
        print(f"    {body.decode('utf-8')}")
        print()

        print("3. Reading the pieces back")
        print("==========================")
        lines = head.decode("ascii").split("\r\n")
        version, status, reason = lines[0].split(" ", 2)
        print(f"    HTTP version : {version}")
        print(f"    status code  : {status}")
        print(f"    reason phrase: {reason}")
        for line in lines[1:]:
            name, _, value = line.partition(": ")
            print(f"    header       : {name} = {value}")
        print()
        print("  That is the entire protocol. Everything `requests` adds is")
        print("  convenience on top of these bytes: building the request line,")
        print("  encoding the query string, pooling the connection, decoding")
        print("  the body, and turning a status code into an exception.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
