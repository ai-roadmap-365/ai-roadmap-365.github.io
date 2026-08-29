# Troubleshooting — Day 018 lab

## `curl: command not found`

Rare on macOS and Linux, where `curl` is preinstalled. Install it with your
Day 13 package manager: `brew install curl` (macOS) or `sudo apt install curl`
(Debian/Ubuntu). Confirm with `curl --version`.

## `httpbin.org` returns `503 Service Temporarily Unavailable` (or times out)

`httpbin.org` is a free, shared, unmetered service, so it occasionally rate-
limits or is briefly overloaded — this is expected, not a mistake on your part.
Options:

- **Retry** in a minute; outages are usually short.
- **Use the mirror** `https://httpbingo.org`, which is a compatible copy of the
  same project and returns the identical `"json"` echo shape. Just swap the
  host: `https://httpbingo.org/post`, `https://httpbingo.org/status/404`.

The reference script (`examples/http_explorer.sh`) and the tests already fall
back to the mirror automatically, and the tests **skip** (never fail) the echo
check if both services are down — a third-party outage is not your fault.

## My `POST` behaves like a `GET` / the body isn't there

You dropped the `-d` flag or its value. `-d '{"hello":"world"}'` does two
things: it supplies the request body **and** switches the method to `POST`.
Add `-v` and read the request line (`> POST /post ...`) to confirm the method.

## The status-code command prints nothing (or glues the number to my prompt)

You likely left out `-o /dev/null` (so the body scrolled past the code) or the
trailing `\n` in `-w "%{http_code}\n"` (so the number has no newline after it).
Use the full form: `curl -s -o /dev/null -w "%{http_code}\n" https://example.com`.

## I see `301` or `302` instead of `200`

You requested an `http://` URL that redirects to `https://` (or a path that
moved). Add `-L` to make `curl` follow redirects, or request the `https://` URL
directly. This is the `3xx` redirection class doing its job.

## The status line says `HTTP/2` but the lesson shows `HTTP/1.1`

Both are correct. `curl` and the server negotiate the newest version they both
support; a modern server behind a CDN answers `HTTP/2` (or `HTTP/3`). The
methods, headers, and status codes are identical across versions — only the
wire format differs.

## `curl -v` floods my screen with HTML

`-v` also prints the response body (the page's HTML). To see only the
request/response *lines*, pipe through a filter and discard the body:
`curl -s -v https://example.com -o /dev/null 2>&1 | grep -E '^[<>]'`.

## No internet / offline

Both scripts detect this: they print `Network reachable: no`, describe what
each step would show, and exit 0. The tests skip the network checks with a
clear message. Reconnect and rerun to do the live exercises.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and follow the Linux path). Native
PowerShell has a `curl` alias that maps to `Invoke-WebRequest` with different
flags, so the commands here will not work as written outside WSL.
