# My Memory Hierarchy — Day 003 worksheet

This worksheet extends the Day 1 machine profile with the levels we could
not see then. Fill in every value from your own machine using the lab
script (`bash starter/measure_read_speed.sh` once completed, or
`bash examples/measure_read_speed.sh`) and, where noted, your Day 1
worksheet. Keep this file — Week 1's project (the Annotated Machine
Teardown) assembles it with the Day 1 profile.

| Level | Your machine's size | Approximate latency (from the lesson table) | Command / source you used |
| ----- | ------------------- | ------------------------------------------- | ------------------------- |
| Registers | ~1 KB total per core (not directly measurable) | | lesson table |
| L1 data cache | | | |
| L2 cache | | | |
| L3 / system-level cache (if reported) | | | |
| RAM | | | Day 1 worksheet or `sysctl -n hw.memsize` |
| Free disk on `/` | | | Day 1 worksheet or `df -h /` |
| Cold read of the 200 MB test file | (seconds and MB/s) | | lab script |
| Warm read of the 200 MB test file | (seconds and MB/s) | | lab script |

## Sanity checks (tick each)

- [ ] Each level's size is bigger than the one above it (L1 < L2 < RAM < disk).
- [ ] My cache sizes are in KiB/MiB, my RAM in GiB, my disk in GB/TB — three
      different unit scales, exactly as the pyramid predicts.
- [ ] My warm read was at least as fast as my cold read, and I can say which
      level of the hierarchy served it.

## My pyramid, in my machine's real numbers

Write one paragraph: starting at the registers and descending to your disk,
tell the story of *your* memory hierarchy with the sizes you measured and an
approximate latency for each level. End with one sentence on what would
happen if you opened a dataset larger than your RAM.

## One thing that surprised me

One or two sentences.
