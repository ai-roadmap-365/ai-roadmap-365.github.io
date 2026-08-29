# Week 01 project — Annotated Machine Teardown

The week's seven labs each measured one layer of your computer. This
project assembles those measurements into a single artifact: **a one-page
annotated architecture diagram of *your* machine**, where every number is
one you measured yourself.

## What you are building

A diagram (hand-drawn and photographed, or made in any drawing tool) of
the layered stack from Day 1's lesson — applications, operating system,
CPU and memory, storage — with your machine's real values written onto
each layer, plus a half-page written walkthrough.

## Inputs (from this week's labs)

| Source | Values to carry over |
| ------ | -------------------- |
| Day 1 `starter/machine-profile-template.md` | CPU model, cores, RAM (GiB and bytes), free disk, OS version |
| Day 2 lab | one instruction trace you executed on the toy CPU (as the "what the CPU does" callout) |
| Day 3 `starter/hierarchy-worksheet.md` | L1/L2 cache sizes, cold vs warm read timings |
| Day 4 lab | your RAM in bytes written in binary-prefix units (GiB) with the conversion shown |
| Day 5 lab | one file's magic bytes as the "everything is bytes" callout |
| Day 6 `starter/os-profile-worksheet.md` | kernel name/version, shell, process count |
| Day 7 `starter/process-worksheet.md` | your shell's PID and parent chain |

## Steps

1. Collect the seven worksheets/values above (rerun any lab if a value is
   missing — every command is in that day's README).
2. Draw the layer stack (Day 1's layers diagram is the map). Annotate each
   layer with your measured values; add one arrow tracing "what happens
   when I run a command" from application down to transistors and back.
3. Write the walkthrough (≤ half a page): your machine described top to
   bottom in your own words, using your numbers.
4. Validate with the checklist below, then keep the artifact — Week 2's
   automation project and later AI-hardware discussions build on it.

## Expected output

- One diagram (photo or file) with, at minimum: CPU model and core count
  on the CPU layer; L1/L2 cache sizes and RAM on the memory layer; free
  disk on the storage layer; OS name, kernel, and process count on the OS
  layer; your shell and its PID on the application layer.
- One written walkthrough of ≤ half a page using at least six of your
  measured values.

## Validation

- [ ] Every number on the diagram came from a command you ran this week
      (no copied spec-sheet values).
- [ ] The layers appear in the correct order and each has ≥1 annotation.
- [ ] The command-journey arrow passes through every layer exactly once.
- [ ] The walkthrough mentions the speed/size trade-off between at least
      two memory levels using your own measurements.
- [ ] A classmate (or you, tomorrow) can answer "what machine is this?"
      from the diagram alone: chip, memory, storage, OS.

## Troubleshooting

Missing a value? Each day's lab README lists the exact command; rerun just
that command. Diagram tooling is irrelevant — paper beats perfect. If your
cache-size commands returned nothing (some Linux VMs), write "not exposed
by this environment" on that layer; honesty beats invention.
