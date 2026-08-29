#!/usr/bin/env bash
# Day 014 lab — completed reference implementation.
#
# Organize a directory by sorting its files into subfolders named for their
# file extension. Designed to be SAFE to run unattended and on a schedule:
#   * --dry-run   previews every action and changes nothing
#   * logging     appends one timestamped line per real move to organize.log
#   * idempotent  a second run moves nothing, because sorted files now live
#                 in subfolders that the top-level scan does not descend into
#
# Usage:
#   organize_files.sh [--dry-run] <directory>
#
# This script only ever touches the directory you give it. It never edits
# your crontab or any system setting.
set -euo pipefail

usage() {
  echo "Usage: $(basename "$0") [--dry-run] <directory>"
  echo "  Sort files in <directory> into subfolders by extension."
  echo "  --dry-run   print what would happen without moving anything"
}

# --- parse arguments -------------------------------------------------------
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

if [ -z "$target" ]; then
  echo "error: no target directory given" >&2
  usage >&2
  exit 2
fi
if [ ! -d "$target" ]; then
  echo "error: not a directory: $target" >&2
  exit 2
fi

log="$target/organize.log"
prefix=""
$dry_run && prefix="[dry-run] "

# Track which extension folders we have already announced in a dry run,
# since dry-run never actually creates the directory.
announced=" "

count=0
for path in "$target"/*; do
  # Only consider regular files that sit directly in the target directory.
  [ -f "$path" ] || continue

  base="$(basename "$path")"

  # Skip our own log file so we never sort the log into a "log/" folder.
  [ "$base" = "organize.log" ] && continue

  # Skip dotfiles and anything without a clear extension (no dot in the name).
  case "$base" in
    .*) continue ;;      # hidden files like .gitkeep
    *.*) : ;;            # has an extension — proceed
    *) continue ;;       # no extension at all — leave it alone
  esac

  # Extension = text after the final dot, lowercased for tidy folder names.
  ext="$(printf '%s' "${base##*.}" | tr '[:upper:]' '[:lower:]')"
  dest="$target/$ext"

  # Announce (dry-run) or create (real) the destination folder once.
  if [ ! -d "$dest" ] && [[ "$announced" != *" $ext "* ]]; then
    if $dry_run; then
      echo "${prefix}would create directory: $dest"
    else
      mkdir -p "$dest"
    fi
    announced="$announced$ext "
  fi

  # Idempotency guard: only move if the file is not already in its folder.
  if [ "$(cd "$(dirname "$path")" && pwd)" = "$(cd "$dest" 2>/dev/null && pwd || echo "$dest")" ]; then
    continue
  fi

  count=$((count + 1))
  if $dry_run; then
    echo "${prefix}would move $base -> $ext/"
  else
    mv "$path" "$dest/"
    echo "moved $base -> $ext/"
    echo "$(date '+%F %T') moved $base -> $ext/" >> "$log"
  fi
done

if $dry_run; then
  echo "${prefix}complete: $count file(s) would be organized, 0 changes made"
else
  echo "complete: $count file(s) organized"
  echo "$(date '+%F %T') run complete: $count file(s) organized" >> "$log"
fi
