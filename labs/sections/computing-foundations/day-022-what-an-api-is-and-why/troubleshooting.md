# Troubleshooting — Day 022 lab

## `curl: (6) Could not resolve host`

Your machine cannot reach the internet — DNS failed (Day 16). Check your
connection and try again; every call in this lab needs network access. The
scripts and tests detect no network and exit 0 with a clear message.

## The JSON prints as one long unindented line

That is the raw response body. Pipe it through `python3 -m json.tool` to
pretty-print it with indentation:

```bash
curl -s https://jsonplaceholder.typicode.com/todos/1 | python3 -m json.tool
```

If Python then reports `Expecting value: line 1 column 1`, the API returned
something that is not JSON (usually a transient error page) — retry in a
moment, and check the URL for a typo.

## httpbin.org times out or returns a 503

`httpbin.org` is a shared free service and is sometimes overloaded. The example
retries transient failures and falls back to a clear message; the test turns a
transient httpbin outage into a **skip**, never a failure. Wait a minute and
re-run — the other two APIs are unaffected. A 503 is itself a real, valid
server response worth recognizing.

## The ISS command "fails" only when I add `https`

Open Notify's ISS endpoint is served over plain `http://`, not `https://`. Use
the URL exactly as written: `http://api.open-notify.org/iss-now.json`. This is
a good reminder that not every service offers TLS (Day 19).

## The httpbin URL breaks in my shell

A URL containing `&` must be **quoted**, or the shell reads `&` as "run in the
background" and mangles the request:

```bash
curl -s "https://httpbin.org/get?course=365-days-of-ai&day=22"   # quotes required
```

## `python3: command not found`

On some minimal Linux setups Python 3 is installed as `python`. Try `python -m
json.tool`, or install `python3` from your package manager (Day 13). On macOS
`python3` is present by default.

## Offline

The scripts and tests detect no network and exit 0 with a message. Connect to
the internet to see live output.
