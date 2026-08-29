#!/usr/bin/env bash
# toy_cpu.sh — a four-instruction toy CPU simulator for the Day 2 lab.
#
# It reads a program file (one instruction per line, '#' starts a comment)
# and executes it exactly the way the lesson describes: fetch the
# instruction at the program counter (PC), advance the PC, decode the
# instruction into an opcode and operands, execute it, and show the
# register state after every step.
#
# Instruction set (opcodes must be uppercase):
#   LOAD Rn,value      put an integer into register Rn
#   ADD Ra,Rb->Rc      add registers Ra and Rb, store the sum in Rc
#   PRINT Rn           send the value of register Rn to the output
#   HALT               stop the machine
#
# Registers: R1 R2 R3 R4, all starting at 0.
#
# Usage: bash toy_cpu.sh <program-file>
#
# Exit codes: 0 = program ran to HALT; 1 = bad instruction or no HALT;
#             2 = usage error (missing or unreadable program file).
set -u

if [ $# -ne 1 ]; then
  echo "usage: bash $0 <program-file>" >&2
  exit 2
fi
program_file="$1"
if [ ! -f "${program_file}" ]; then
  echo "error: program file not found: ${program_file}" >&2
  exit 2
fi

# --- machine state -----------------------------------------------------
R1=0; R2=0; R3=0; R4=0
PC=0
executed=0
halted=no

die() {
  # PC has already advanced past the fetched instruction, so report PC-1.
  echo "ERROR at PC=$((PC - 1)): $1" >&2
  exit 1
}

is_reg() {
  case "$1" in
    R1 | R2 | R3 | R4) return 0 ;;
    *) return 1 ;;
  esac
}

reg_value() {
  # Caller must have validated the name with is_reg first.
  eval "printf '%s' \"\$$1\""
}

set_reg() {
  eval "$1=\$2"
}

is_int() {
  case "$1" in
    '' | -) return 1 ;;
    -*) case "${1#-}" in *[!0-9]* | '') return 1 ;; *) return 0 ;; esac ;;
    *[!0-9]*) return 1 ;;
    *) return 0 ;;
  esac
}

# --- load the program into "memory" (a bash array) ---------------------
program=()
while IFS= read -r raw || [ -n "${raw}" ]; do
  line="${raw%%#*}"                              # strip comments
  line="${line#"${line%%[![:space:]]*}"}"        # trim leading whitespace
  line="${line%"${line##*[![:space:]]}"}"        # trim trailing whitespace
  [ -z "${line}" ] && continue
  program[${#program[@]}]="${line}"
done < "${program_file}"

if [ "${#program[@]}" -eq 0 ]; then
  echo "error: ${program_file} contains no instructions" >&2
  exit 2
fi

echo "=== Toy CPU ==="
echo "Program: ${program_file} (${#program[@]} instructions in memory)"
echo "Registers start at: R1=0 R2=0 R3=0 R4=0"
echo

# --- the fetch-decode-execute loop --------------------------------------
while [ "${PC}" -lt "${#program[@]}" ]; do
  instr="${program[${PC}]}"
  printf 'PC=%s  FETCH    %s\n' "${PC}" "${instr}"
  PC=$((PC + 1))                                 # PC advances right after fetch

  case "${instr}" in
    *' '*) op="${instr%% *}"; args="${instr#* }" ;;
    *) op="${instr}"; args="" ;;
  esac
  args="$(printf '%s' "${args}" | tr -d '[:space:]')"

  case "${op}" in
    LOAD)
      dest="${args%%,*}"
      value="${args#*,}"
      [ "${dest}" = "${args}" ] && die "LOAD needs the form: LOAD Rn,value"
      is_reg "${dest}" || die "unknown register '${dest}' (valid: R1 R2 R3 R4)"
      is_int "${value}" || die "'${value}' is not an integer"
      printf '      DECODE   opcode=LOAD  dest=%s  value=%s\n' "${dest}" "${value}"
      set_reg "${dest}" "${value}"
      printf '      EXECUTE  %s <- %s\n' "${dest}" "${value}"
      ;;
    ADD)
      case "${args}" in
        *,*'->'*) ;;
        *) die "ADD needs the form: ADD Ra,Rb->Rc" ;;
      esac
      src1="${args%%,*}"
      rest="${args#*,}"
      src2="${rest%%->*}"
      dest="${rest#*->}"
      is_reg "${src1}" || die "unknown register '${src1}' (valid: R1 R2 R3 R4)"
      is_reg "${src2}" || die "unknown register '${src2}' (valid: R1 R2 R3 R4)"
      is_reg "${dest}" || die "unknown register '${dest}' (valid: R1 R2 R3 R4)"
      v1="$(reg_value "${src1}")"
      v2="$(reg_value "${src2}")"
      sum=$((v1 + v2))
      printf '      DECODE   opcode=ADD  src1=%s  src2=%s  dest=%s\n' "${src1}" "${src2}" "${dest}"
      set_reg "${dest}" "${sum}"
      printf '      EXECUTE  %s <- %s + %s = %s + %s = %s\n' "${dest}" "${src1}" "${src2}" "${v1}" "${v2}" "${sum}"
      ;;
    PRINT)
      reg="${args}"
      [ -n "${reg}" ] || die "PRINT needs the form: PRINT Rn"
      is_reg "${reg}" || die "unknown register '${reg}' (valid: R1 R2 R3 R4)"
      printf '      DECODE   opcode=PRINT  reg=%s\n' "${reg}"
      printf '      EXECUTE  send %s to the output\n' "${reg}"
      printf 'OUTPUT: %s\n' "$(reg_value "${reg}")"
      ;;
    HALT)
      printf '      DECODE   opcode=HALT\n'
      printf '      EXECUTE  stop the clock\n'
      executed=$((executed + 1))
      halted=yes
      break
      ;;
    *)
      die "unknown opcode '${op}' (valid: LOAD ADD PRINT HALT)"
      ;;
  esac

  executed=$((executed + 1))
  printf '      REGS     R1=%s R2=%s R3=%s R4=%s\n\n' "${R1}" "${R2}" "${R3}" "${R4}"
done

echo
if [ "${halted}" = yes ]; then
  echo "HALT reached after ${executed} instructions."
  echo "Final registers: R1=${R1} R2=${R2} R3=${R3} R4=${R4}"
else
  echo "ERROR: the program ended without HALT — a real CPU would keep fetching whatever bits sit in the next memory cells and try to execute them." >&2
  exit 1
fi
