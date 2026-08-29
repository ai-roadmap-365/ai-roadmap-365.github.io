# Required profile sections and fields (all platforms)

A correct run of `explore_os.sh` prints, in order:

1. `=== Meet Your Operating System ===`
2. `Generated on: YYYY-MM-DD`
3. `--- Kernel ---` with `Kernel line (uname -a): <full uname -a line>` beginning `Darwin` (macOS) or `Linux`
4. `--- Uptime ---` with an `Uptime:` line containing the up-duration and load averages
5. `--- Identity ---` with `Logged-in user: <username>` and `Login shell: </path/to/shell>`
6. `--- Mounted filesystems ---` with the `df -h` header and data row for `/`
7. `--- Top 5 processes by memory ---` with up to five rows: user, PID, %MEM, command (trimmed to 60 chars)
8. `--- Where the kernel lives ---` (see platform differences below)
9. `=== End of OS profile ===`

No field may read `unknown` in a completed solution.

`sample-macos.txt` in this directory is a real captured run (macOS, Apple
Silicon, 2026-07-12). A Linux capture is deliberately not included — this
lab was executed on macOS, and we do not fabricate output. On Linux, expect
these honest differences:

- **Kernel line** begins `Linux <hostname> <release> ...` and the release
  looks like `6.8.0-xx-generic`; `Kernel name and release` reads
  `Linux 6.8.0-...`.
- **Uptime** format differs slightly by distribution (`up 3 days, 2:14` and
  similar variations).
- **Login shell** is typically `/bin/bash` rather than macOS's `/bin/zsh`.
- **Mounted filesystems**: the count is usually higher (Linux mounts many
  virtual filesystems such as `tmpfs`, `proc`, `sysfs`); the root row names
  a device like `/dev/sda2` or `/dev/nvme0n1p2` and shows sizes in `G`
  rather than `Gi` on some distributions.
- **Top processes**: same columns; typical top entries are browsers,
  desktop services, or — on servers — daemons like `mysqld`.
- **Where the kernel lives**: prints
  `Linux kernel image found at: /boot/vmlinuz-<release>` with its size
  (tens of MB). On WSL or inside a container there is usually no
  `/boot/vmlinuz*`, and the script honestly prints
  `No /boot/vmlinuz* image visible from this environment.` with an
  explanation — that output is correct, not a failure.
