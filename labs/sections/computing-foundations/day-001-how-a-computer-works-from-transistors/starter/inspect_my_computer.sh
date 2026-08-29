#!/usr/bin/env bash
# Day 001 lab — inspect your own computer from the command line.
#
# This starter script already detects your operating system and prints the
# report skeleton. Your job (README, "Your task" section) is to fill in each
# exercise below with the single command that prints the value, replacing the
# `unknown` assignments. The completed reference version is in
# examples/inspect_my_computer_completed.sh — try it yourself first.
set -euo pipefail

os="$(uname -s)"

echo "=== My Machine Profile ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Operating system kernel: ${os}"

if [ "${os}" = "Darwin" ]; then
  # Exercise 1 (macOS): set cpu_model using: sysctl -n machdep.cpu.brand_string
  cpu_model="unknown"
  # Exercise 2 (macOS): set cpu_cores using: sysctl -n hw.ncpu
  cpu_cores="unknown"
  # Exercise 3 (macOS): set ram_bytes using: sysctl -n hw.memsize
  ram_bytes="unknown"
  # Exercise 4 (macOS): set os_version using: sw_vers -productVersion
  os_version="unknown"
elif [ "${os}" = "Linux" ]; then
  # Exercise 1 (Linux): set cpu_model using: lscpu | grep 'Model name' (clean it with sed or awk)
  cpu_model="unknown"
  # Exercise 2 (Linux): set cpu_cores using: nproc
  cpu_cores="unknown"
  # Exercise 3 (Linux): set ram_bytes by reading MemTotal from /proc/meminfo (value is in kB — multiply by 1024)
  ram_bytes="unknown"
  # Exercise 4 (Linux): set os_version from PRETTY_NAME in /etc/os-release
  os_version="unknown"
else
  echo "Unsupported OS for this script: ${os} (Windows users: see the README's PowerShell section)" >&2
  exit 1
fi

# Exercise 5 (both): set disk_free for / using: df -h / (take the 'Avail' column of the data row)
disk_free="unknown"

echo "CPU model: ${cpu_model}"
echo "CPU cores: ${cpu_cores}"
if [ "${ram_bytes}" != "unknown" ]; then
  echo "RAM: $((ram_bytes / 1073741824)) GiB (${ram_bytes} bytes)"
else
  echo "RAM: unknown"
fi
echo "Free disk on /: ${disk_free}"
echo "OS version: ${os_version}"
echo "=== End of profile ==="
