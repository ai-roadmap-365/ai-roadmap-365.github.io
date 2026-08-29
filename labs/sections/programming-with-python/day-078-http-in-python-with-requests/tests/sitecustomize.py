"""A guard that makes "this lab never touches the internet" a fact, not a claim.

Python imports `sitecustomize` automatically at interpreter start-up if it can
find it on the import path. `tests/run_tests.sh` puts this directory on
PYTHONPATH for one check, then runs the whole example suite under it. Any
attempt to resolve a hostname or connect to an address that is not the
loopback interface raises immediately and fails the run.

If you ever add an example that talks to a real site, this file will tell you
in the least ambiguous way available.
"""

from __future__ import annotations

import socket

LOOPBACK = {"127.0.0.1", "::1", "0.0.0.0", ""}

_real_connect = socket.socket.connect
_real_connect_ex = socket.socket.connect_ex
_real_getaddrinfo = socket.getaddrinfo


class NetworkBlocked(RuntimeError):
    """Raised instead of opening a connection to anything but the loopback."""


def _check(address: object) -> None:
    if isinstance(address, tuple) and address:
        host = address[0]
        if isinstance(host, str) and host not in LOOPBACK:
            raise NetworkBlocked(f"blocked a connection to {host!r} — this lab is offline")


def _connect(self, address):  # type: ignore[no-untyped-def]
    _check(address)
    return _real_connect(self, address)


def _connect_ex(self, address):  # type: ignore[no-untyped-def]
    _check(address)
    return _real_connect_ex(self, address)


def _getaddrinfo(host, *args, **kwargs):  # type: ignore[no-untyped-def]
    if isinstance(host, str) and host not in LOOPBACK:
        raise NetworkBlocked(f"blocked a name lookup for {host!r} — this lab is offline")
    return _real_getaddrinfo(host, *args, **kwargs)


socket.socket.connect = _connect  # type: ignore[method-assign]
socket.socket.connect_ex = _connect_ex  # type: ignore[method-assign]
socket.getaddrinfo = _getaddrinfo  # type: ignore[assignment]
