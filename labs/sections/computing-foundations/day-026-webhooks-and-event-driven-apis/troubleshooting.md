# Troubleshooting — Day 026 lab

## My signature does not match `cadd3bf8...e3c0`

Almost always a trailing newline. Use `printf '%s' "$PAYLOAD"` (not `echo`,
which appends `\n`) so the bytes you sign are exactly the payload bytes. Also
confirm you used the identical payload string and the identical secret — a
single changed byte in either flips the whole signature.

## `openssl: command not found`

Install it (`brew install openssl` on macOS, `sudo apt install openssl` on
Debian/Ubuntu); it is preinstalled on nearly all systems. The signature step
needs it.

## `openssl` prints `HMAC-SHA256(stdin)= <hex>` instead of just the hex

Different openssl builds format the label differently. The scripts strip
everything up to `= ` with `sed 's/^.*= //'`, which handles all the common
formats. If you are running the command by hand, pipe it through that `sed`
to keep only the digest.

## The delivery step prints "could not reach httpbin"

`httpbin.org` is a shared free service and frequently returns gateway errors
or resets connections under load. The scripts already retry with backoff
(`--retry ... --retry-all-errors`). If it still fails, wait a minute and
re-run — the signature and verify steps do not need the network and always
work. A failed delivery is not your bug.

## The test reports a `skip` on the network check

That is expected and fine: offline (or when httpbin is transiently down) the
live delivery check is skipped, never failed. The local HMAC checks still run
and must pass. `0 failure(s)` is a pass whether there are skips or not.

## The retry loop always shows 503, 503, 200

That is intentional — the loop uses a fixed, simulated sequence of statuses so
the demo is deterministic and needs no flaky server to fail on purpose. It
shows the *shape* of at-least-once retrying: keep trying on non-2xx, stop on a
2xx acknowledgement.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and follow the same steps), or run
the individual `openssl` and `curl` commands in a shell that has them.
