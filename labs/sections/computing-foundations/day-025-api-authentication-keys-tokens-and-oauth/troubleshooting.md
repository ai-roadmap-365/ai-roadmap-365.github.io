# Troubleshooting — Day 025 lab

## Every request prints `000`

`000` from `curl -w '%{http_code}'` means no HTTP response arrived — you are
offline, or a proxy/firewall is blocking the request. Check connectivity with
`curl -s -o /dev/null -w '%{http_code}\n' https://httpbin.org/status/200`. The
scripts and tests detect this and skip the live requests, exiting 0.

## A request prints `503`

`httpbin.org` is a shared free service and is occasionally overloaded,
returning `503 Service Temporarily Unavailable`. That is the server, not your
credential. Wait a minute and retry; the scripts already pass
`--retry 5 --retry-delay 2` to ride past brief outages, and the test script
treats a transient 5xx as a SKIP rather than a failure.

## Basic auth prints `401` even with `user:pass`

The path and the credentials must agree: `/basic-auth/user/pass` expects
username `user` and password `pass`, exactly what `-u user:pass` sends. Check
for a typo, and make sure you did not change one without the other.

## `$DEMO_TOKEN` comes through empty

You either opened a new shell after `export`, or mistyped the variable name.
Run the `export DEMO_TOKEN=...` line and the `curl` line in the *same* shell,
and confirm with `echo "$DEMO_TOKEN"` before sending.

## `curl: command not found`

Install curl: macOS ships it; on Debian/Ubuntu run `sudo apt install curl`, on
Fedora `sudo dnf install curl`. Verify with `curl --version`.

## `Permission denied` when running a script

Run it through bash explicitly: `bash starter/auth_demo.sh`. You do not need to
mark it executable; if you prefer `./starter/auth_demo.sh`, first run
`chmod +x starter/auth_demo.sh`.

## The bearer endpoint returned `401` instead of `200`

httpbin's `/bearer` endpoint requires the header format to be exactly
`Authorization: Bearer <token>` with a non-empty token. Check the header
spelling and that a token follows `Bearer ` (with one space).

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu) or Git Bash, and run the Linux
commands unchanged. The scripts are plain `curl` and behave identically there.
