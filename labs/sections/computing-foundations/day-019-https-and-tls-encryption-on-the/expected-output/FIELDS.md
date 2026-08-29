# Required output fields (all platforms)

A correct online run of `inspect_tls.sh` prints, in order:

1. `=== TLS inspection for <host> ===`
2. `Generated on: YYYY-MM-DD`
3. `--- Certificate (openssl) ---`
4. `subject=...` — the domain the certificate is for
5. `issuer=...` — the CA that signed the certificate
6. `notBefore=...` — start of the validity window
7. `notAfter=...` — expiry of the validity window
8. `--- Handshake summary (curl) ---`
9. A `SSL connection using TLSv1.x ...` line — the negotiated TLS version and cipher
10. `subject:`, `issuer:`, and `expire date:` lines from curl
11. `SSL certificate verify ok.` — chain of trust verified
12. `=== End of inspection ===`

`sample-example-com.txt` in this directory is a real captured run against
`example.com` (macOS, OpenSSL 3.x, 2026-07-12). The exact issuer, dates, and
cipher change whenever the site renews its certificate — the *shape* is what
stays constant.

## Platform differences (not fabricated — described)

- **Linux** produces the same fields. The `curl` verbose lines may be
  prefixed with connection markers like `* (IN)` / `* (OUT)`; the field
  names (`subject:`, `issuer:`, `expire date:`) are identical.
- **OpenSSL vs LibreSSL.** macOS has historically shipped LibreSSL as
  `/usr/bin/openssl` and Homebrew installs OpenSSL 3.x. Both support the
  `s_client`, `x509 -subject -issuer -dates`, and `-showcerts` flags used
  here; if a flag is rejected, run `openssl x509 -help` for your build's
  exact spelling. The capture above is from OpenSSL 3.x.
- **Offline.** With no network, the script prints the `OFFLINE or host
  unreachable` message and exits 0 instead of the certificate fields.
- **Windows.** Use WSL and follow the Linux path, or use Git Bash which
  bundles both `openssl` and `curl`.
