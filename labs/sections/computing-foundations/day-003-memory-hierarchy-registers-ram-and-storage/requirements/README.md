# Dependencies — Day 003 lab

**None beyond a POSIX shell.** Everything this lab uses ships with the OS:

- `bash` ≥ 3.2 (preinstalled on macOS and Linux)
- `sysctl` and `sw_vers` (macOS) or the `/sys/devices/system/cpu/.../cache/`
  and `/proc/meminfo` files (Linux) for cache and RAM sizes
- `dd`, `date`, `df` for the read-speed measurement

No installs, no package manager, no network. On Windows, run under WSL or
read cache sizes with PowerShell (see `../troubleshooting.md`).
