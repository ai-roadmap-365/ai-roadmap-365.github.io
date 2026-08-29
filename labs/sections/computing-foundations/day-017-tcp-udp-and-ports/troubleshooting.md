# Troubleshooting — Day 017 lab

## `lsof` shows fewer ports than I expected

Without `sudo`, `lsof` only reports sockets your own user owns, and macOS may
hide some system services. **That is fine** — this lab is deliberately
read-only and never asks for elevated privileges. You will still see your own
listening services (editors, dev servers, sync agents). Running with `sudo`
would reveal more, but the course's rule is: don't `sudo` a script you are
learning from.

## `command not found: lsof` (or `ss`, or `netstat`)

The script tries `lsof`, then `ss`, then `netstat`, and prints a clear
message if none is present. To install one:

- Linux (Debian/Ubuntu): `sudo apt install iproute2` (for `ss`) or
  `sudo apt install lsof`
- Linux (Fedora/RHEL): `sudo dnf install iproute` or `sudo dnf install lsof`
- macOS: `lsof` is preinstalled; nothing to do.

## `command not found: nc`

Install netcat: `sudo apt install netcat-openbsd` (Debian/Ubuntu),
`sudo dnf install nmap-ncat` (Fedora/RHEL). macOS ships `nc` already. If you
skip it, you still get the listening-port listing; only the loopback probe is
missing.

## A port I can see listening reports "closed" in the loopback test

Some services bind only to the **IPv6** loopback `[::1]`, not the IPv4
loopback `127.0.0.1`. A `nc -z 127.0.0.1 <port>` probe cannot reach an
IPv6-only listener, so it reports closed even though the service is up. Probe
the IPv6 loopback instead: `nc -z -w 1 ::1 <port>`. This is a real networking
subtlety, not a mistake in the lab.

## The loopback test says port 1 is "connection refused"

That is the intended demonstration. Port 1 has nothing listening on a normal
machine, so the kernel immediately refuses the connection — the exact meaning
of the "connection refused" error you will meet again and again.

## `nc -z 127.0.0.1 5000` succeeds but no dev server is running (macOS)

On macOS, the AirPlay receiver / Control Center often holds ports `5000` and
`7000`. If you need those ports for your own server, turn off "AirPlay
Receiver" in System Settings → General → AirDrop & Handoff.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open your Linux distro and follow the Linux
path), or, in PowerShell, list ports with `netstat -an | findstr LISTENING`
and test a port with `Test-NetConnection -ComputerName 127.0.0.1 -Port <n>`.
