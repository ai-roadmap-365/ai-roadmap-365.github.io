# Required fields in the measurements report

Both `examples/measure_read_speed.sh` and a completed
`starter/measure_read_speed.sh` must print, on any supported platform:

| Line prefix | Meaning | Example (real macOS run) |
| --- | --- | --- |
| `=== Memory Hierarchy Measurements ===` | report header | — |
| `Generated on:` | run date | `Generated on: 2026-07-12` |
| `Operating system kernel:` | `Darwin` (macOS) or `Linux` | `Operating system kernel: Darwin` |
| `L1 data cache:` | bytes and KiB | `L1 data cache: 131072 bytes (128 KiB)` |
| `L2 cache:` | bytes and MiB | `L2 cache: 16777216 bytes (16 MiB)` |
| `RAM:` | bytes and GiB | `RAM: 38654705664 bytes (36 GiB)` |
| `Cold read (first pass):` | seconds and MB/s | `Cold read (first pass):  0.023 s (8695 MB/s)` |
| `Warm read (second pass):` | seconds and MB/s | `Warm read (second pass): 0.022 s (9090 MB/s)` |
| `Warm read speed-up over cold:` | ratio | `Warm read speed-up over cold: 1.0x` |
| `=== End of measurements ===` | report footer | — |
| `Test file removed.` | cleanup confirmation (printed by the EXIT trap) | — |

Notes on interpreting your own run:

- The cache and RAM values differ per machine; what must hold everywhere is
  the *shape*: L1 in KiB, L2 in MiB, RAM in GiB.
- On Apple Silicon the script reports the performance-core caches
  (`hw.perflevel0.*`); on Intel Macs the plain `hw.l1dcachesize` /
  `hw.l2cachesize` names; on Linux, cpu0's sysfs cache descriptors.
- A speed-up near 1.0x is normal on machines with plenty of free RAM: the
  test file is still in the page cache from being written, so even the
  "cold" read is served from RAM. See `troubleshooting.md` for how to
  observe a truly cold read.
- The warm read must never be much slower than the cold read; the automated
  test allows a 1.5x noise tolerance.
