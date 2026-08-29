#!/usr/bin/env bash
# Day 006 lab — completed reference implementation.
# A guided tour of your operating system from the terminal: kernel, uptime,
# identity, shell, filesystems, top memory consumers, and where the kernel
# itself lives on disk. Supports macOS (Darwin) and Linux (including WSL);
# Windows users run this inside WSL.
#
# Note: we use `set -eu` here, deliberately without `pipefail` — pipelines
# like `ps aux | sort | head` end with head closing the pipe early, which
# is normal and expected, not an error.
set -eu

os="$(uname -s)"

echo "=== Meet Your Operating System ==="
echo "Generated on: $(date '+%Y-%m-%d')"

echo "--- Kernel ---"
echo "Kernel line (uname -a): $(uname -a)"
echo "Kernel name and release: $(uname -s) $(uname -r)"

echo "--- Uptime ---"
echo "Uptime:$(uptime)"

echo "--- Identity ---"
echo "Logged-in user: $(whoami)"
echo "Login shell: ${SHELL}"

echo "--- Mounted filesystems ---"
mount_count="$(df -h | tail -n +2 | wc -l | tr -d ' ')"
echo "Mounted filesystems reported by df: ${mount_count}"
echo "Root filesystem (mounted on /):"
df -h / | sed 's/^/  /'

echo "--- Top 5 processes by memory ---"
# Column 4 of `ps aux` is %MEM on both macOS and Linux; sort by it, descending.
echo "  USER          PID   %MEM  COMMAND"
ps aux | sort -k4 -nr | head -5 | awk '{
  cmd = $11; for (i = 12; i <= NF; i++) cmd = cmd " " $i;
  printf "  %-12s %6s  %4s%%  %.60s\n", $1, $2, $4, cmd
}'

echo "--- Where the kernel lives ---"
if [ "${os}" = "Darwin" ]; then
  kernel_path="/System/Library/Kernels/kernel"
  if [ -f "${kernel_path}" ]; then
    echo "macOS kernel (XNU) found at: ${kernel_path}"
    ls -lh "${kernel_path}" | awk '{print "  size: " $5 "  owner: " $3}'
  else
    echo "macOS kernel file not found at ${kernel_path} on this system."
    echo "(Some macOS versions relocate it; the kernel is still running — you are using it right now.)"
  fi
elif [ "${os}" = "Linux" ]; then
  kernel_image="$(ls /boot/vmlinuz* 2>/dev/null | head -n 1 || true)"
  if [ -n "${kernel_image}" ]; then
    echo "Linux kernel image found at: ${kernel_image}"
    ls -lh "${kernel_image}" | awk '{print "  size: " $5 "  owner: " $3}'
  else
    echo "No /boot/vmlinuz* image visible from this environment."
    echo "(Common and honest on WSL and in containers: the running kernel is supplied from outside this filesystem.)"
  fi
else
  echo "Unsupported OS for this script: ${os} (Windows users: run this inside WSL)" >&2
  exit 1
fi

echo "=== End of OS profile ==="
