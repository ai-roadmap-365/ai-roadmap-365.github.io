#!/usr/bin/env bash
# Day 003 lab — measure your machine's memory levels (YOUR working file).
#
# This starter already detects your OS, creates and cleans up the test file,
# and prints the report skeleton. Your job is the four numbered exercises
# below: replace each "unknown" assignment with the exact command named in
# the comment above it, wrapped in "$(...)". The completed reference is in
# examples/measure_read_speed.sh — run it first to see where you are headed.
#
# The script runs as-is (printing "unknown" for unfinished parts), makes no
# network connections, needs no elevated privileges, and writes only the
# temporary test file inside this lab directory.
set -euo pipefail
export LC_ALL=C

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
test_file="${lab_dir}/read-speed-testfile.bin"
size_mb=200

cleanup() {
  if [ -f "${test_file}" ]; then
    rm -f "${test_file}"
    echo "Test file removed."
  fi
}
trap cleanup EXIT

os="$(uname -s)"

# Helper (Linux): convert a sysfs cache size such as "48K" or "2048K" to bytes.
sysfs_cache_bytes() {
  local raw
  raw="$(cat "$1" 2>/dev/null || echo '')"
  case "${raw}" in
    *K) echo $(( ${raw%K} * 1024 )) ;;
    *M) echo $(( ${raw%M} * 1048576 )) ;;
    *[0-9]) echo "${raw}" ;;
    *) echo 0 ;;
  esac
}

echo "=== Memory Hierarchy Measurements ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Operating system kernel: ${os}"

if [ "${os}" = "Darwin" ]; then
  # Exercise 1 (macOS): set l1d_bytes using:
  #   sysctl -n hw.perflevel0.l1dcachesize 2>/dev/null || sysctl -n hw.l1dcachesize
  # (performance-core figure on Apple Silicon; plain name on Intel Macs)
  l1d_bytes="unknown"
  # Exercise 2 (macOS): set l2_bytes using:
  #   sysctl -n hw.perflevel0.l2cachesize 2>/dev/null || sysctl -n hw.l2cachesize
  l2_bytes="unknown"
  # Exercise 3 (macOS): set ram_bytes using: sysctl -n hw.memsize
  ram_bytes="unknown"
elif [ "${os}" = "Linux" ]; then
  # Exercise 1 (Linux): set l1d_bytes using the provided helper on cpu0's
  # level-1 Data cache descriptor:
  #   sysfs_cache_bytes /sys/devices/system/cpu/cpu0/cache/index0/size
  # (index0 is the L1 data cache on almost all machines; confirm with
  #  `cat /sys/devices/system/cpu/cpu0/cache/index0/type` — it should say Data)
  l1d_bytes="unknown"
  # Exercise 2 (Linux): set l2_bytes using:
  #   sysfs_cache_bytes /sys/devices/system/cpu/cpu0/cache/index2/size
  # (index2 is L2 on almost all machines; its `level` file should say 2)
  l2_bytes="unknown"
  # Exercise 3 (Linux): set ram_bytes by reading MemTotal (in kB) and
  # multiplying by 1024:
  #   mem_kb="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"; ram_bytes=$(( mem_kb * 1024 ))
  ram_bytes="unknown"
else
  echo "Unsupported OS for this script: ${os} (Windows users: run it inside WSL)" >&2
  exit 1
fi

if [ "${l1d_bytes}" != "unknown" ]; then
  echo "L1 data cache: ${l1d_bytes} bytes ($(( l1d_bytes / 1024 )) KiB)"
else
  echo "L1 data cache: unknown"
fi
if [ "${l2_bytes}" != "unknown" ]; then
  echo "L2 cache: ${l2_bytes} bytes ($(( l2_bytes / 1048576 )) MiB)"
else
  echo "L2 cache: unknown"
fi
if [ "${ram_bytes}" != "unknown" ]; then
  echo "RAM: ${ram_bytes} bytes ($(( ram_bytes / 1073741824 )) GiB)"
else
  echo "RAM: unknown"
fi

echo "Creating a ${size_mb} MB test file with dd (inside this lab directory) ..."
if [ "${os}" = "Darwin" ]; then dd_bs="1m"; else dd_bs="1M"; fi
dd if=/dev/zero of="${test_file}" bs="${dd_bs}" count="${size_mb}" 2>/dev/null
sync

# Exercise 4 (both): time a cold and a warm read of the test file.
# Set cold_s and then warm_s, IN THAT ORDER, each using exactly:
#   { time cat "${test_file}" > /dev/null; } 2>&1
# (TIMEFORMAT below makes bash's `time` print just the elapsed seconds;
# the first assignment measures the cold read, the second the warm one.)
TIMEFORMAT='%R'
cold_s="unknown"
warm_s="unknown"

if [ "${cold_s}" = "unknown" ] || [ "${warm_s}" = "unknown" ]; then
  echo "Cold read (first pass):  unknown"
  echo "Warm read (second pass): unknown"
  echo "(Exercise 4 not completed yet.)"
else
  rate_of() { awk -v mb="${size_mb}" -v s="$1" 'BEGIN { if (s + 0 <= 0) print "n/a"; else printf "%d", mb / s }'; }
  echo "Cold read (first pass):  ${cold_s} s ($(rate_of "${cold_s}") MB/s)"
  echo "Warm read (second pass): ${warm_s} s ($(rate_of "${warm_s}") MB/s)"
  speedup="$(awk -v c="${cold_s}" -v w="${warm_s}" 'BEGIN { if (w + 0 <= 0) print "n/a"; else printf "%.1f", c / w }')"
  echo "Warm read speed-up over cold: ${speedup}x"
fi
echo "=== End of measurements ==="
