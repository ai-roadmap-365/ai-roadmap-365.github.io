#!/usr/bin/env bash
# Day 009 lab — build and explore a file tree (YOUR working file).
#
# The workspace machinery (a temporary directory created UNDER this lab
# directory, plus a trap that deletes it on exit) is already written for you
# and is SAFE: nothing outside the workspace is ever touched.
#
# Your task: complete the five numbered exercises below. Each one names the
# EXACT command to use in its comment. Replace the single placeholder line in
# each exercise (the one that echoes a marker) with that command. The completed
# reference version is in examples/explore_files.sh — try it yourself first,
# then compare.
#
# Note: this starter uses `set -u` (not the stricter `set -euo pipefail` of the
# reference) so that it still runs to completion while exercises are only partly
# filled in. Once every placeholder is replaced, it behaves exactly like the
# reference.
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace="$(mktemp -d "${lab_dir}/tmp.explore.XXXXXX")"
cleanup() { rm -rf "${workspace}"; }
trap cleanup EXIT

echo "=== Build and Explore a File Tree ==="
echo "Workspace: ${workspace}"
echo

cd "${workspace}"

# --- Exercise 1: print the working directory -------------------------------
# Replace the next line with the command:  pwd
echo -n "Working directory (pwd): "
echo "REPLACE-ME-1"
echo

# --- Exercise 2: build a nested directory tree -----------------------------
# Replace the next line with the command:  mkdir -p project/data
echo "REPLACE-ME-2"
echo "Created nested directories with: mkdir -p project/data"
echo

cd project

# --- Exercise 3: create two empty files ------------------------------------
# Replace the next line with the command:  touch data/notes.txt report.md
echo "REPLACE-ME-3"
echo "Contents of $(pwd) (ls):"
ls
echo
echo "Long listing including hidden entries (ls -la):"
ls -la
echo

# --- Exercise 4: make a file executable ------------------------------------
touch run.sh
chmod 644 run.sh          # normalize starting permissions (given)
echo "Before chmod:"
ls -l run.sh
# Replace the next line with the command:  chmod 754 run.sh
echo "REPLACE-ME-4"
echo "After chmod:"
ls -l run.sh
echo

# --- Exercise 5: move a file into the data directory -----------------------
# Replace the next line with the command:  mv report.md data/
echo "REPLACE-ME-5"
echo "Moved report.md into data/ with: mv report.md data/"
echo "Current directory now contains (ls):"
ls
echo "data/ now contains (ls data):"
ls data
echo

echo "=== Done ==="
echo "The trap will now remove ${workspace}, leaving nothing behind."
