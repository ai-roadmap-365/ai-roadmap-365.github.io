# What a correct run shows (all platforms)

`sample-run.txt` in this directory is a **real captured run** (macOS, curl
8.7.1, 2026-07-12). Your run will differ in the details below, but the shape
is fixed.

A correct run prints, in order:

1. `=== HTTP Explorer ===` and `Network reachable: yes` (or `no` when offline).
2. **Step 1** — the request lines (each starting `>`) and the response status
   line and headers (each starting `<`). The status line reads `HTTP/2 200` or
   `HTTP/1.1 200 OK` depending on which version curl and the server negotiate;
   both are correct. The dates, `age`, and `cf-ray` values change every run.
3. **Step 2** — `Status code: 200`.
4. **Step 3** — the JSON echo, whose key part is:

   ```text
     "json": {
       "hello": "world"
     }
   ```

5. **Step 4** — `Status code: 404`.
6. `=== End of HTTP Explorer ===`.

## About the echo service (httpbin.org vs the mirror)

The lesson and exercises use **`https://httpbin.org`** as the canonical free
test service. It is shared and unmetered, so it sometimes returns `503 Service
Temporarily Unavailable` or times out. When that happens the reference script
automatically falls back to **`https://httpbingo.org`**, the compatible mirror
of the same project, which returns the identical `"json"` echo shape. That is
why the captured `sample-run.txt` shows `Using echo service:
https://httpbingo.org` — httpbin.org was busy at capture time. When httpbin.org
is up, the `Host` in the POST/404 URLs reads `httpbin.org` instead; everything
else is the same.

## Offline behavior

With no network reachable, the script prints `Network reachable: no`, lists
what each step *would* show, and exits 0. No captured file is needed for that
path; it produces no live output by design.
