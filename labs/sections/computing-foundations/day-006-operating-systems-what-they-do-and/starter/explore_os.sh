#!/usr/bin/env bash
# Day 006 lab — meet your operating system from the command line.
#
# This starter script already prints the report skeleton and handles the
# OS-specific "where is the kernel" section for you. Your job is to complete
# the five numbered exercises below, replacing each `unknown` assignment with
# the command named in the comment, in `$(...)` form. The completed reference
# version is in examples/explore_os.sh — try it yourself first.
#
# Note: we use `set -eu` here, deliberately without `pipefail` — pipelines
# like `ps aux | sort | head` end with head closing the pipe early, which
# is normal and expected, not an error.
set -eu

os="$(uname -s)"
if [ "${os}" != "Darwin" ] && [ "${os}" != "Linux" ]; then
  echo "Unsupported OS for this script: ${os} (Windows users: run this inside WSL)" >&2
  exit 1
fi

echo "=== Meet Your Operating System ==="
echo "Generated on: $(date '+%Y-%m-%d')"

echo "--- Kernel ---"
# Exercise 1: set kernel_line using: uname -a
#   (uname asks the kernel to describe itself: name, release, architecture.)
kernel_line="unknown"
echo "Kernel line (uname -a): ${kernel_line}"

echo "--- Uptime ---"
# Exercise 2: set up_line using: uptime
#   (how long the kernel has been running since boot, plus load averages.)
up_line="unknown"
echo "Uptime: ${up_line}"

echo "--- Identity ---"
# Exercise 3a: set current_user using: whoami
current_user="unknown"
# Exercise 3b: set login_shell from the SHELL environment variable: echo "$SHELL"
#   (hint: you do not even need a command — "${SHELL}" is already the value.)
login_shell="unknown"
echo "Logged-in user: ${current_user}"
echo "Login shell: ${login_shell}"

echo "--- Mounted filesystems ---"
# Exercise 4: set root_fs to the df -h report for the root filesystem: df -h /
#   (both header and data row; keep the quotes so the newline survives.)
root_fs="unknown"
echo "Root filesystem (mounted on /):"
echo "${root_fs}" | sed 's/^/  /'

echo "--- Top 5 processes by memory ---"
# Exercise 5: set top_procs using: ps aux | sort -k4 -nr | head -5
#   (ps aux lists every process; column 4 is %MEM; sort -k4 -nr orders by it,
#   biggest first; head -5 keeps the top five.)
top_procs="unknown"
echo "${top_procs}" | awk '{
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
else
  kernel_image="$(ls /boot/vmlinuz* 2>/dev/null | head -n 1 || true)"
  if [ -n "${kernel_image}" ]; then
    echo "Linux kernel image found at: ${kernel_image}"
    ls -lh "${kernel_image}" | awk '{print "  size: " $5 "  owner: " $3}'
  else
    echo "No /boot/vmlinuz* image visible from this environment."
    echo "(Common and honest on WSL and in containers: the running kernel is supplied from outside this filesystem.)"
  fi
fi

echo "=== End of OS profile ==="
