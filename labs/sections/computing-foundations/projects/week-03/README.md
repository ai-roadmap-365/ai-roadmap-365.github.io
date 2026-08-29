# Week 03 project — Request Journey Map

This week you followed a web request from your keyboard to a server and
back, layer by layer. This project makes that journey concrete: you trace
**one real page load end to end** with the tools from Days 15–21 and
document every hop.

## What you are building

A one-page "journey map" — a diagram plus a short written trace — of what
happens when you load a single URL of your choice, backed by real command
output you captured yourself.

## Tools you will use (all from this week)

`dig` (DNS), `ping`/`traceroute` (routing and latency), `curl -v` and
`curl -w` (TCP connect, TLS handshake, HTTP request/response, timings),
`openssl s_client` (the certificate), and your browser's DevTools Network
tab (the full waterfall). Everything is free and already installed.

## Steps

1. Pick a public website (a site you use, or `example.com`).
2. **DNS:** `dig +short <host>` — record the resolved IP(s).
3. **Routing/latency:** `ping -c 3 <host>` and a short `traceroute <host>` —
   record the round-trip time and roughly how many hops.
4. **TCP + TLS + HTTP timings:** run the Day 15/21 curl `-w` command and
   record DNS, connect, TLS, and total times.
5. **Certificate:** `openssl s_client`/`curl -vI` — record the issuer and
   expiry (Day 19).
6. **HTTP:** `curl -I <url>` — record the status code and Content-Type
   (Day 18).
7. **Rendering:** open the page in a browser, open DevTools → Network, and
   note the first request, its status, and how many follow-up requests the
   page makes (Day 20).
8. Draw the journey (keyboard → DNS → TCP → TLS → HTTP → server → response →
   render) and annotate each stop with your real numbers.
9. Write a short paragraph tracing the request in your own words.

## Expected output

- A journey diagram (hand-drawn photo or any tool) with your real values on
  each stop: resolved IP, RTT, hop count, DNS/connect/TLS/total times,
  cert issuer + expiry, HTTP status + Content-Type, and follow-up request
  count.
- A half-page written trace in your own words.
- The raw captured command output saved alongside (paste into a text file).

## Validation

- [ ] Every value on the map came from a command you ran (not guessed).
- [ ] The stops appear in the correct order (DNS → TCP → TLS → HTTP →
      render).
- [ ] DNS time, connect time, TLS time, and total time are distinguished
      (not conflated).
- [ ] The certificate issuer and expiry are recorded from a real inspection.
- [ ] The HTTP status code and Content-Type are correct for your URL.
- [ ] You can explain, in one sentence each, what happens at every stop.

## Troubleshooting

- `ping`/`traceroute` may be blocked by some networks or hosts — that does
  not mean the site is down; note it and rely on curl's timings instead.
- If `openssl s_client` hangs, add `</dev/null` to close the input (Day 19).
- httpbin.org or a chosen site may rate-limit — wait and retry, or switch to
  `example.com`.
- Redact any headers before sharing your capture: `curl -v` output can
  include cookies or tokens if you tested an authenticated site.
