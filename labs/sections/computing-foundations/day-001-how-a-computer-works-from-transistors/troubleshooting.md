# Troubleshooting — Day 001 lab

## `sysctl: unknown oid` or `command not found: sw_vers`

You are running the macOS commands on Linux (or vice versa). The script chooses the right branch automatically via `uname -s`; if you are typing commands manually, use the section of the lesson matching your OS.

## `command not found: lscpu` (Linux)

Minimal containers and some distros omit `util-linux`. Install it (`sudo apt install util-linux` on Debian/Ubuntu) or read the model name directly: `grep 'model name' /proc/cpuinfo | head -n 1`.

## `Permission denied` when running the script

You don't need to make it executable — run it through bash explicitly: `bash starter/inspect_my_computer.sh`. If you prefer `./starter/inspect_my_computer.sh`, first run `chmod +x starter/inspect_my_computer.sh`.

## The RAM number looks absurdly large

`sysctl -n hw.memsize` and `/proc/meminfo` report **bytes** and **kB** respectively. The script converts to GiB by dividing bytes by 1073741824 (1024³). If you see the raw number, you replaced the whole `echo` line instead of only the `ram_bytes="unknown"` assignment — restore the file (`git checkout -- starter/inspect_my_computer.sh`) and edit only the assignments.

## My GiB value doesn't match the GB on the box my computer came in

Manufacturers use decimal gigabytes (10⁹ bytes); operating systems usually use binary gibibytes (2³⁰ bytes). 16 GB decimal ≈ 14.9 GiB binary. Both are "right"; the units differ. The Day 4 lesson (binary and data representation) covers this properly.

## Tests fail with `no field is left 'unknown'`

That check is telling you an exercise is still unfinished — search the starter for `"unknown"` and complete the remaining assignments.

## Windows: `bash` is not recognized

Use WSL (`wsl --install`, then open Ubuntu and follow the Linux path), or skip the script and run the PowerShell equivalents from the lesson's hands-on section, filling the worksheet manually.
