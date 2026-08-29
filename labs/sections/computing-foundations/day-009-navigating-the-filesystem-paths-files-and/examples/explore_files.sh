#!/usr/bin/env bash
# Day 009 lab — completed reference implementation.
# Builds a small sample directory tree inside a temporary workspace created
# UNDER this lab directory, navigates it with pwd/cd/ls, creates and moves
# files, makes one file executable with chmod (showing the before/after
# `ls -l`), and then removes the whole temporary tree on exit via a trap.
#
# Nothing outside the temporary workspace is ever touched. Safe to re-run.
set -euo pipefail

# The lab directory is the parent of this script's directory (examples/..).
lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create the temporary workspace INSIDE the lab directory, and register a
# trap so it is deleted whether the script succeeds, fails, or is interrupted.
workspace="$(mktemp -d "${lab_dir}/tmp.explore.XXXXXX")"
cleanup() { rm -rf "${workspace}"; }
trap cleanup EXIT

echo "=== Build and Explore a File Tree ==="
echo "Workspace: ${workspace}"
echo

# --- 1. Where are we, and build a small tree -------------------------------
cd "${workspace}"
echo "Working directory (pwd): $(pwd)"
mkdir -p project/data
echo "Created nested directories with: mkdir -p project/data"
echo

# --- 2. Create files and list the tree -------------------------------------
cd project
touch data/notes.txt report.md
echo "Created files: data/notes.txt and report.md"
echo "Contents of $(pwd) (ls):"
ls
echo
echo "Long listing including hidden entries (ls -la):"
ls -la
echo

# --- 3. Make a file executable and show the before/after -------------------
touch run.sh
chmod 644 run.sh          # normalize starting permissions for a stable demo
echo "Before chmod:"
ls -l run.sh
chmod 754 run.sh          # owner rwx, group r-x, other r-- => octal 754
echo "After chmod:"
ls -l run.sh
echo "The permission string changed to -rwxr-xr-- (octal 754): the execute bit is now set."
echo

# --- 4. Move a file and confirm its new location ---------------------------
mv report.md data/
echo "Moved report.md into data/ with: mv report.md data/"
echo "Current directory now contains (ls):"
ls
echo "data/ now contains (ls data):"
ls data
echo

echo "=== Done ==="
echo "The trap will now remove ${workspace}, leaving nothing behind."
