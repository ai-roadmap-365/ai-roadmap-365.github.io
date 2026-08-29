#!/usr/bin/env bash
# Day 001 lab — completed reference implementation.
# Prints a machine profile: CPU, cores, RAM, free disk, OS version.
# Supports macOS (Darwin) and Linux; Windows users use the PowerShell
# commands in the README (or run this under WSL).
set -euo pipefail

os="$(uname -s)"

echo "=== My Machine Profile ==="
echo "Generated on: $(date '+%Y-%m-%d')"
echo "Operating system kernel: ${os}"

if [ "${os}" = "Darwin" ]; then
  cpu_model="$(sysctl -n machdep.cpu.brand_string)"
  cpu_cores="$(sysctl -n hw.ncpu)"
  ram_bytes="$(sysctl -n hw.memsize)"
  os_version="macOS $(sw_vers -productVersion)"
elif [ "${os}" = "Linux" ]; then
  cpu_model="$(lscpu | sed -n 's/^Model name:[[:space:]]*//p' | head -n 1)"
  cpu_cores="$(nproc)"
  mem_kb="$(sed -n 's/^MemTotal:[[:space:]]*\([0-9]*\) kB/\1/p' /proc/meminfo)"
  ram_bytes="$((mem_kb * 1024))"
  os_version="$(sed -n 's/^PRETTY_NAME="\(.*\)"/\1/p' /etc/os-release)"
else
  echo "Unsupported OS for this script: ${os} (Windows users: see the README's PowerShell section)" >&2
  exit 1
fi

disk_free="$(df -h / | awk 'NR==2 {print $4}')"

echo "CPU model: ${cpu_model}"
echo "CPU cores: ${cpu_cores}"
echo "RAM: $((ram_bytes / 1073741824)) GiB (${ram_bytes} bytes)"
echo "Free disk on /: ${disk_free}"
echo "OS version: ${os_version}"
echo "=== End of profile ==="
