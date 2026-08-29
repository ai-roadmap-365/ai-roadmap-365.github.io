#!/usr/bin/env bash
# OPTIONAL exercise — needs a type checker that is NOT part of this lab.
#
# Nothing in this lab requires an install or a network connection. This
# script looks for a static type checker and, if it finds one, runs it over
# examples/scoring.py (which contains two deliberate type errors). If it
# finds none, it explains what you would have seen and exits 0 so the lab
# still completes cleanly.
#
# Run from the lab directory:  bash examples/check_types.sh
set -u

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${lab_dir}/examples/scoring.py"

find_checker() {
  for name in mypy pyright; do
    if command -v "${name}" >/dev/null 2>&1; then
      echo "${name}"
      return 0
    fi
  done
  if python3 -c "import mypy" >/dev/null 2>&1; then
    echo "python3 -m mypy"
    return 0
  fi
  return 1
}

if checker="$(find_checker)"; then
  echo "Type checker found: ${checker}"
  echo "Checking examples/scoring.py (it contains two deliberate errors) ..."
  echo
  # A checker exits non-zero when it finds errors. Here that is the SUCCESS
  # case, so the exit status is reported rather than propagated.
  ${checker} "${target}"
  echo
  echo "(A non-zero exit above is expected: the file has two planted errors.)"
else
  echo "No static type checker is installed, so this optional step is skipped."
  echo
  echo "This lab needs no installs and no network, so that is a normal result."
  echo "A checker reads examples/scoring.py WITHOUT running it and reports"
  echo "the two planted contradictions between the annotations and the code:"
  echo "  * label() promises to return str but returns record.score, a float"
  echo "  * main() passes one EvalRecord where mean_score wants list[EvalRecord]"
  echo
  echo "Python itself reports neither on import: run"
  echo "  python3 examples/inspect_runtime.py"
  echo "to see what the interpreter actually stores and what it never checks."
fi

exit 0
