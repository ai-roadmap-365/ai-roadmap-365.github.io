# Required output lines (all platforms)

A correct online run of `examples/auth_demo.sh` prints, in order:

1. `=== API Authentication Demo ===`
2. Basic auth, correct credentials: `HTTP status: 200`
3. Basic auth, wrong credentials: `HTTP status: 401`
4. Bearer endpoint: JSON with `"authenticated": true` and `"token": "token-example-123"`
5. Headers endpoint: JSON echoing your `X-Api-Key: demo-key` (httpbin normalizes the
   header name's capitalization to `X-Api-Key`)
6. Env-var bearer: JSON with `"authenticated": true` and `"token": "token-from-env-example"`
7. `=== End of demo ===`

`sample-run.txt` in this directory is a real captured run (macOS, curl 8.7.1,
online, 2026-07-12).

## Platform notes

- **Linux** produces byte-for-byte the same output; only the `User-Agent`
  string (the local curl version) and the `X-Amzn-Trace-Id` value differ.
- **Windows** users run the same commands in WSL or Git Bash; native
  PowerShell uses `Invoke-RestMethod` with `-Headers`, which is out of scope
  for this lab.
- The `X-Amzn-Trace-Id` value is assigned fresh by httpbin on every request,
  so it will never match the sample exactly — that is expected.
- If any request prints `503`, httpbin is transiently overloaded (a shared
  free service). That is the server, not your credential; retry shortly. The
  test script treats a transient 5xx as a SKIP, not a failure.
