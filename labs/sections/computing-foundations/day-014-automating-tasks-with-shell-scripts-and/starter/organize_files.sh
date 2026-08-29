#!/usr/bin/env bash
# Day 014 lab — YOUR working file.
#
# Build a safe file-organizing script step by step. The skeleton already
# parses arguments and loops over the directory's files; your job is to fill
# in the five numbered exercises below so the script sorts files by extension,
# supports a --dry-run preview, logs its moves, and is safe to run twice.
#
# The completed reference version is in examples/organize_files.sh — try to
# finish this yourself first, then compare.
#
# Usage:  organize_files.sh [--dry-run] <directory>
#
# This script must ONLY touch the directory you give it. It never edits your
# crontab or any system setting.
set -euo pipefail

usage() {
  echo "Usage: $(basename "$0") [--dry-run] <directory>"
}

# --- argument parsing (already done for you) -------------------------------
dry_run=false
target=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=true ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "error: unknown option: $arg" >&2; usage >&2; exit 2 ;;
    *)  target="$arg" ;;
  esac
done

if [ -z "$target" ] || [ ! -d "$target" ]; then
  echo "error: give one existing directory to organize" >&2
  usage >&2
  exit 2
fi

log="$target/organize.log"
prefix=""
$dry_run && prefix="[dry-run] "
announced=" "
count=0

for path in "$target"/*; do
  [ -f "$path" ] || continue
  base="$(basename "$path")"
  [ "$base" = "organize.log" ] && continue

  # Exercise 1 (SKIP FILES WITH NO EXTENSION):
  #   Skip dotfiles (names starting with '.') and any file with no dot in its
  #   name, so files without a clear extension are left alone. Use a `case`:
  #     case "$base" in .*) continue ;; *.*) : ;; *) continue ;; esac
  case "$base" in
    .*) continue ;;
    *) : ;;            # <-- replace this line to also skip names with no dot
  esac

  # Exercise 2 (COMPUTE THE EXTENSION AND DESTINATION):
  #   Set `ext` to the text after the final dot, lowercased, and `dest` to a
  #   subfolder of "$target" named for that extension. Hints:
  #     ext="$(printf '%s' "${base##*.}" | tr '[:upper:]' '[:lower:]')"
  #     dest="$target/$ext"
  ext="unknown"
  dest="$target/$ext"

  # Exercise 3 (CREATE OR ANNOUNCE THE FOLDER):
  #   If the destination does not exist and has not been announced yet, then
  #   in dry-run mode print   "${prefix}would create directory: $dest"
  #   and in real mode run    mkdir -p "$dest"
  #   Record it:              announced="$announced$ext "
  if [ ! -d "$dest" ] && [[ "$announced" != *" $ext "* ]]; then
    : # <-- add the dry-run echo / real mkdir here, then record it in announced
    announced="$announced$ext "
  fi

  count=$((count + 1))

  # Exercise 4 (MOVE OR PREVIEW, WITH LOGGING):
  #   In dry-run mode print   "${prefix}would move $base -> $ext/"
  #   In real mode:           mv "$path" "$dest/"
  #                           echo "moved $base -> $ext/"
  #                           and append a timestamped line to "$log":
  #                           echo "$(date '+%F %T') moved $base -> $ext/" >> "$log"
  if $dry_run; then
    : # <-- print the "would move" line
  else
    : # <-- move the file, echo it, and append to the log
  fi
done

# Exercise 5 (PRINT THE SUMMARY):
#   In dry-run mode print:  "${prefix}complete: $count file(s) would be organized, 0 changes made"
#   In real mode print:     "complete: $count file(s) organized"
#   (and, in real mode, append the same summary to "$log")
if $dry_run; then
  echo "(exercise 5: print the dry-run summary here)"   # <-- replace this line
else
  echo "(exercise 5: print the real-run summary here)"  # <-- replace this line
fi
