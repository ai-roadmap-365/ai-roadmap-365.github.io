# Troubleshooting — Day 003 lab

## `sysctl: unknown oid 'hw.perflevel0.l1dcachesize'`

That name exists only on Apple Silicon. The script already falls back to the
plain `hw.l1dcachesize` / `hw.l2cachesize` names on Intel Macs — if you are
running the commands by hand, use the plain names.

## Cache sizes come back empty on Linux

Minimal or virtualized Linux (containers, some cloud VMs) may not expose
`/sys/devices/system/cpu/cpu0/cache/`. The script prints `not exposed by
this environment` for any level it cannot read — that is honest and
expected; note it on your worksheet rather than inventing a number.
`lscpu | grep -i cache` is an alternative source when it is available.

## Warm read is not faster than cold read

This is normal and the lab allows for it. On a fast SSD with a warm OS cache
already primed, or on a machine with plenty of free RAM, both passes can be
near-identical — the ratio may read `1.0x`. The point is to *observe* the
page-cache mechanism, not to hit a target speed-up. If you want a clearer
gap, increase `size_mb` in the script to something close to (but below) your
free RAM, or on Linux drop caches between passes with
`sync; echo 3 | sudo tee /proc/sys/vm/drop_caches` (optional, needs sudo —
skip it if you would rather not).

## `dd: No space left on device`

The script writes a ~200 MB temporary file inside the lab directory and
deletes it on exit. If your disk is nearly full, lower `size_mb` at the top
of the script (e.g. to 50) and rerun.

## The test file was left behind after I pressed Ctrl+C

The cleanup runs on normal exit via a `trap`. A hard kill can occasionally
skip it; just delete `read-speed-testfile.bin` in the lab directory manually.

## Windows

Run the scripts inside WSL (they work unchanged), or read your cache sizes
in PowerShell with `Get-CimInstance Win32_CacheMemory | Select-Object
Purpose, InstalledSize` and record the numbers on the worksheet by hand.
