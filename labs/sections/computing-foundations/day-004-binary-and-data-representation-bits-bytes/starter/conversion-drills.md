# Day 004 drill sheet — conversions by hand

Work every drill **on paper first**, showing your steps in the space under
each one. Only then check yourself with the listed command (run from this
lab's directory, using either your completed starter toolkit or the
reference in `examples/`). The full worked answer key lives with the
instructor materials — resist looking until all twelve are done.

Method reminders from the lesson:

- **Decimal → binary:** subtract the largest power of 2 that fits, repeat
  (or divide by 2 repeatedly and read the remainders bottom-to-top).
- **Binary → decimal:** add the place values (128 64 32 16 8 4 2 1) under
  the 1-bits.
- **Hex → binary:** replace each hex digit with its 4-bit group; no
  arithmetic needed.
- **Addition:** columns from the right; 1 + 1 = 10, so write 0, carry 1.
- **Two's complement negation:** flip every bit, then add 1.

## Part A — decimal to binary

**Drill 1.** Convert **13** to binary.

    work:

    answer: ________            check: bash examples/binary_toolkit.sh d2b 13

**Drill 2.** Convert **42** to binary.

    work:

    answer: ________            check: bash examples/binary_toolkit.sh d2b 42

**Drill 3.** Convert **91** to binary.

    work:

    answer: ________            check: bash examples/binary_toolkit.sh d2b 91

**Drill 4.** Convert **200** to binary.

    work:

    answer: ________            check: bash examples/binary_toolkit.sh d2b 200

## Part B — binary to decimal

**Drill 5.** Convert **1011** to decimal.

    work:

    answer: ________            check: bash examples/binary_toolkit.sh b2d 1011

**Drill 6.** Convert **10010110** to decimal.

    work:

    answer: ________            check: bash examples/binary_toolkit.sh b2d 10010110

**Drill 7.** Convert **11111111** to decimal.

    work:

    answer: ________            check: bash examples/binary_toolkit.sh b2d 11111111

## Part C — hexadecimal to binary

**Drill 8.** Convert **0x2F** to an 8-bit binary pattern (digit by digit —
no arithmetic).

    work:

    answer: ________            check: bash examples/binary_toolkit.sh h2b 2F

**Drill 9.** Convert **0xB4** to an 8-bit binary pattern.

    work:

    answer: ________            check: bash examples/binary_toolkit.sh h2b B4

## Part D — 8-bit addition with carries

Show the carry row above each sum, as in the lesson's worked examples.

**Drill 10.** Add **01011101 + 00100110**. Give the 8-bit result and verify
it in decimal.

    carries:
              0 1 0 1 1 1 0 1
            + 0 0 1 0 0 1 1 0
            -----------------
    answer: ________           check: convert both inputs with b2d, add in
                                      decimal, then d2b the total

**Drill 11.** Add **10011001 + 01101100**. Give the 8-bit result **and**
state what happened to the ninth bit — treating the inputs as unsigned,
did this addition overflow?

    carries:
              1 0 0 1 1 0 0 1
            + 0 1 1 0 1 1 0 0
            -----------------
    answer: ________           check: b2d both inputs, add in decimal, and
                                      compare against b2d of your 8-bit answer

## Part E — two's complement

**Drill 12.** Using 8-bit two's complement, find the bit pattern for
**−44** (start from 44 = 00101100: flip every bit, add 1). Then prove your
answer by adding it to 00101100 and showing the result is zero once the
ninth bit falls off.

    work:

    answer: ________           check: your pattern read as unsigned should
                                      equal 256 − 44; confirm with b2d
