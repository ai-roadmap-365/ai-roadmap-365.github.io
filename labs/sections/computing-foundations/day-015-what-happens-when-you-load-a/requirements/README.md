# Dependencies — Day 015 lab

**A POSIX shell and three standard network tools.** This lab installs
nothing of its own:

- `bash` ≥ 3.2 (preinstalled on macOS and every mainstream Linux distribution).
- `dig` — DNS lookup tool. Preinstalled on macOS. On minimal Linux images it
  may live in a package: `dnsutils` (Debian/Ubuntu) or `bind-utils`
  (Fedora/RHEL). If you cannot install it, the lesson and troubleshooting
  notes give `nslookup` and `host` as drop-in alternatives.
- `ping` — round-trip probe. Preinstalled on macOS and Linux. **Note:** in
  some container images `ping` needs the `CAP_NET_RAW` capability or root, and
  many networks block ping (ICMP) entirely. A blocked or missing `ping` does
  not stop the lab — the script and tests continue and simply skip that value.
- `curl` — HTTP client. Preinstalled on macOS and most Linux systems
  (`apt install curl` / `dnf install curl` if absent).

There is deliberately no `requirements.txt`/`package.json` here; the tools are
part of a normal developer system. The lab needs a network connection for live
values, but its tests are written to run and pass offline as well, skipping the
network-dependent checks.
