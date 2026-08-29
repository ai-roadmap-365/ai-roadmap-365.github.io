#!/usr/bin/env bash
# Day 003 lab — completed reference: measure your machine's memory levels.
#
# Part 1 reads the L1/L2 cache and RAM sizes from the OS.
# Part 2 creates a ~200 MB test file INSIDE THIS LAB DIRECTORY with dd,
# times a first (cold) and second (warm) read of it to show the OS
# page-cache effect, and always deletes the file afterwards (trap on EXIT).
#
# No network access, no elevated privileges, no writes outside this directory.
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

# Convert a Linux sysfs cache size such as "48K" or "2048K" to bytes.
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
  # Apple Silicon reports per-cluster sizes; prefer the performance cores
  # (hw.perflevel0.*) and fall back to the plain names on Intel Macs.
  l1d_bytes="$(sysctl -n hw.perflevel0.l1dcachesize 2>/dev/null || sysctl -n hw.l1dcachesize)"
  l2_bytes="$(sysctl -n hw.perflevel0.l2cachesize 2>/dev/null || sysctl -n hw.l2cachesize)"
  ram_bytes="$(sysctl -n hw.memsize)"
elif [ "${os}" = "Linux" ]; then
  # Walk cpu0's cache descriptors: level 1 Data cache and level 2 cache.
  l1d_bytes=0
  l2_bytes=0
  for idx in /sys/devices/system/cpu/cpu0/cache/index*; do
    [ -d "${idx}" ] || continue
    level="$(cat "${idx}/level" 2>/dev/null || echo 0)"
    ctype="$(cat "${idx}/type" 2>/dev/null || echo '')"
    if [ "${level}" = "1" ] && [ "${ctype}" != "Instruction" ] && [ "${l1d_bytes}" = "0" ]; then
      l1d_bytes="$(sysfs_cache_bytes "${idx}/size")"
    fi
    if [ "${level}" = "2" ] && [ "${l2_bytes}" = "0" ]; then
      l2_bytes="$(sysfs_cache_bytes "${idx}/size")"
    fi
  done
  mem_kb="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
  ram_bytes=$(( mem_kb * 1024 ))
else
  echo "Unsupported OS for this script: ${os} (Windows users: run it inside WSL)" >&2
  exit 1
fi

echo "L1 data cache: ${l1d_bytes} bytes ($(( l1d_bytes / 1024 )) KiB)"
echo "L2 cache: ${l2_bytes} bytes ($(( l2_bytes / 1048576 )) MiB)"
echo "RAM: ${ram_bytes} bytes ($(( ram_bytes / 1073741824 )) GiB)"

echo "Creating a ${size_mb} MB test file with dd (inside this lab directory) ..."
if [ "${os}" = "Darwin" ]; then dd_bs="1m"; else dd_bs="1M"; fi
dd if=/dev/zero of="${test_file}" bs="${dd_bs}" count="${size_mb}" 2>/dev/null
sync

# TIMEFORMAT='%R' makes bash's built-in `time` print just the elapsed
# seconds; `cat` streams the file to /dev/null so only reading is measured.
TIMEFORMAT='%R'
cold_s=$( { time cat "${test_file}" > /dev/null; } 2>&1 )
warm_s=$( { time cat "${test_file}" > /dev/null; } 2>&1 )

rate_of() { awk -v mb="${size_mb}" -v s="$1" 'BEGIN { if (s + 0 <= 0) print "n/a"; else printf "%d", mb / s }'; }
cold_rate="$(rate_of "${cold_s}")"
warm_rate="$(rate_of "${warm_s}")"
speedup="$(awk -v c="${cold_s}" -v w="${warm_s}" 'BEGIN { if (w + 0 <= 0) print "n/a"; else printf "%.1f", c / w }')"

echo "Cold read (first pass):  ${cold_s} s (${cold_rate} MB/s)"
echo "Warm read (second pass): ${warm_s} s (${warm_rate} MB/s)"
echo "Warm read speed-up over cold: ${speedup}x"
echo "If the two times are close, the file was already in the page cache from being written — see troubleshooting.md."
echo "=== End of measurements ==="
