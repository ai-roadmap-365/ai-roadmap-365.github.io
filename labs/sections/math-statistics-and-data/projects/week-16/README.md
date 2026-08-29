# Week 16 project — Gradient Descent Visualizer

This week was **Linear Algebra II and Calculus**: eigenvalues and
eigenvectors, norms and distances, derivatives, partial derivatives and
gradients, the chain rule, gradient descent from scratch, and visualizing
optimization. Split across two days, those look like two subjects. They are
one subject: **the eigenvalues of the Hessian decide how hard the descent
is**, and this project is where you prove that to yourself instead of taking
it on faith.

Day 111 built gradient descent by hand and measured what learning-rate
regimes do to it. Day 112 drew contour maps, loss curves and animated GIFs
with Pillow. This project joins the two into a small tool, then asks it to
survive surfaces that punish a naive implementation — including the one
pathological case every optimisation course eventually has to confront.

**Environment constraint:** matplotlib, scipy and pandas are **not**
available in this environment. NumPy and Pillow are. So every image in this
project is drawn with Pillow, exactly as on Day 112, and no library optimiser
may be used anywhere — `scipy.optimize` does not exist here, and even if it
did, using it would defeat the point. The descent is yours.

## What you are building

A command-line **gradient descent visualizer**: given a loss surface and an
optimiser, it runs the descent from a starting point, records every step,
and produces a contour map with the path drawn on it, an animated GIF of the
descent, and a loss curve on a log axis. Run across several surfaces and
optimisers, it also produces a comparison table and a learning-rate sweep.

```
python descend.py --surface bowl --optimizer momentum --lr 0.1 --steps 200 --out runs/bowl-momentum
```

The point is not the picture. It is that by the end you can look at a
contour map's eccentricity and predict, before running anything, roughly how
many steps plain gradient descent will need — because you have watched the
condition number and the step count move together.

## Requirements

- **Your own optimisers, from scratch** (Day 111): plain gradient descent,
  gradient descent with momentum, and one adaptive method you choose
  yourself — RMSProp or Adam. No `scipy.optimize`, no library optimiser of
  any kind. If you are unsure whether something counts as "the library doing
  the optimisation," it does.
- **Analytic gradients, verified by central differences.** A gradient check
  is part of the tool, not a one-off script you ran once and deleted. Day 111
  showed a central-difference check catching a sign error that looked, from
  the loss curve alone, like a tuning problem. Your tool should be able to
  report, for any surface, the max absolute difference between the analytic
  gradient and the central-difference estimate at a handful of sample points.
- **At least three surfaces**, of increasing cruelty:
  1. a **well-conditioned bowl** (a quadratic with nearly equal eigenvalues)
     — where everything works, so you know what success looks like;
  2. an **ill-conditioned bowl** (a quadratic with very unequal eigenvalues)
     — where plain descent visibly zig-zags and the step count scales with
     the condition number;
  3. a **pathological case** — Rosenbrock's function is the canonical
     choice, with its minimum at (1, 1) inside a long curved valley. Add a
     saddle point as a second pathological case if you have time: plain
     descent stalls near a saddle in a way momentum escapes, which is a
     sharper demonstration than Rosenbrock alone.
- **Condition number from the Hessian's eigenvalues** (Day 106), computed and
  reported alongside the measured step count for every run, so the
  connection is demonstrated, not asserted. For a quadratic bowl the Hessian
  is constant and the condition number is exact. For Rosenbrock the Hessian
  varies with position — evaluate it at a specific point (the start, and
  separately at the minimum) and say which point you used and why the two
  differ.
- **A contour map with the descent path drawn on it**, via Pillow, for every
  run.
- **An animated GIF of the descent**, via Pillow, whose frame count equals
  the number of recorded steps.
- **A loss curve on a log axis**, so the reader can look at the picture and
  say whether convergence is geometric (a straight line on a log axis) or
  something else.
- **A learning-rate sweep** on at least one surface, producing the
  characteristic U-shape — too small converges slowly, too large diverges,
  and there is an interior optimum. Divergent runs must not crash the sweep:
  a step that overflows to `inf` and then produces `nan` is expected
  behaviour for a learning rate that is too large, and your tool must detect
  and record that as "diverged," not let it propagate into a crash or a
  silently broken plot.
- **A comparison table**: for every surface × optimiser combination, the
  step count to a stated tolerance, the final loss, and whether it converged
  at all.
- **A CLI** with a `--dry-run` flag that prints the resolved configuration
  (surface, optimiser, hyperparameters, starting point) and the output paths
  it would write, without writing anything.
- **`NOTES.md`** recording: which optimiser won on which surface and why you
  think so; the condition numbers you measured; and one thing the pictures
  showed you that the numbers alone had not.

## Steps

1. Implement one surface — the well-conditioned bowl — and its analytic
   gradient. Write the central-difference check first and run it before you
   trust anything else.
2. Implement plain gradient descent and get it converging on the bowl. This
   is the easy case; it should take very few steps.
3. Compute the bowl's Hessian eigenvalues by hand (they are the diagonal, if
   you set the bowl up as a diagonal quadratic) and confirm your code's
   reported condition number matches.
4. Add the ill-conditioned bowl by changing the eigenvalues, and watch plain
   descent zig-zag. Confirm the step count moves with the condition number
   before you touch momentum.
5. Add momentum. Confirm it needs fewer steps than plain descent on the
   ill-conditioned bowl, and that a poorly chosen momentum coefficient can
   make things worse, not better — measure a couple of values rather than
   picking one and moving on.
6. Add your chosen adaptive method (RMSProp or Adam). Run the gradient check
   again on all three optimisers — the check is on the gradient function,
   not the optimiser, but a bug in how you apply the gradient can look
   identical to a bug in the gradient itself.
7. Add Rosenbrock and, if time allows, the saddle point. Expect a plain
   descent run on Rosenbrock to take dramatically more steps than the bowl
   ever needed, and expect plain descent to stall visibly near the saddle
   while momentum does not.
8. Add the contour map, the GIF and the log-axis loss curve, all via Pillow.
9. Add the learning-rate sweep, handling overflow deliberately.
10. Add the CLI and `--dry-run` last, once every code path it can invoke
    already works.

## Expected output

- The well-conditioned bowl converges in a small number of steps under all
  three optimisers; this is the baseline against which everything else is
  judged.
- The ill-conditioned bowl's step count for plain descent rises as the
  condition number rises. The exact numbers depend on the eigenvalues and
  learning rate you chose, so state your parameters alongside any figure —
  do not expect a fixed step count to appear here, expect the *trend* to
  hold.
- Rosenbrock reaches (1, 1) to a tolerance you state, and takes noticeably
  more steps than either bowl — the shape of that gap is the result, not a
  specific number, since it depends on your starting point and learning
  rate.
- Plain descent stalls measurably near the saddle (loss barely decreases for
  many consecutive steps) while momentum moves through it faster.
- The log-axis loss curve is close to a straight line for the quadratic
  bowls and visibly not straight for Rosenbrock, because Rosenbrock's valley
  is not a quadratic bowl and its convergence is not geometric throughout.
- The learning-rate sweep shows an interior optimum: some middle learning
  rate reaches the tolerance in the fewest steps, with both smaller and
  larger rates doing worse (larger rates eventually diverging outright).
- The GIF's frame count equals the number of recorded steps for that run.
- `--dry-run` prints the configuration and the paths it would write, and
  writes nothing — confirm this by checking the output directory is empty
  afterward.

## Validation

- [ ] Plain gradient descent, momentum, and one adaptive method are all
      implemented from scratch; no library optimiser is called anywhere.
- [ ] Every surface's analytic gradient is checked against central
      differences, and the check is part of the tool, not a deleted script.
- [ ] At least three surfaces exist: a well-conditioned bowl, an
      ill-conditioned bowl, and a pathological case (Rosenbrock at minimum).
- [ ] The condition number is computed from the Hessian's eigenvalues for
      every surface, and for Rosenbrock you state which point it was
      evaluated at.
- [ ] The ill-conditioned bowl's step count is shown to move with the
      condition number, not just asserted to.
- [ ] A contour map with the path, an animated GIF, and a log-axis loss
      curve are produced for at least one run, all via Pillow.
- [ ] The GIF's frame count equals the number of recorded steps.
- [ ] A learning-rate sweep is run, and a divergent run is detected and
      recorded rather than crashing the sweep.
- [ ] A comparison table covers every surface × optimiser combination with
      step count, final loss, and convergence status.
- [ ] `--dry-run` prints configuration and output paths and writes no files.
- [ ] `NOTES.md` names a winning optimiser per surface with a reason, states
      the condition numbers measured, and names one thing the pictures
      showed that the numbers alone had not.

## Troubleshooting

- The path runs off the edge of the plot? The plot bounds were fixed to the
  surface's natural extent rather than expanded to fit the path. Compute the
  bounds from the recorded path (with margin) after the run, not before it.
- The optimiser looks "broken" — loss increases, or bounces without
  settling? Run the gradient check before touching the optimiser's code. A
  wrong analytic gradient produces exactly this symptom and is the most
  common cause of a "broken optimiser" in this project.
- Rosenbrock "isn't converging"? Check the loss is still decreasing, just
  slowly, before concluding anything is wrong. The valley is long and
  curved; slow is the expected behaviour, not a bug, and this is exactly why
  it is the pathological case.
- You see overflow warnings and stop there, treating them as a crash? An
  overflow to `inf` on a diverging learning rate is data, not an error —
  catch it, record the run as diverged, and continue the sweep.
- Momentum makes things worse, not better? Measure your momentum
  coefficient rather than trusting a default. Day 111 found a high momentum
  coefficient oscillating worse than plain descent on one surface, while a
  lower one won — the lesson was to measure, not to assume a textbook
  default transfers.
- The contour map or GIF looks upside down or mirrored vertically? A
  world-to-pixel transform that does not flip the y axis. Image rows
  increase downward; the mathematics you are plotting increases upward.
  Flip explicitly when you convert coordinates to pixels.
- Every frame in the GIF looks identical? The path array was mutated in
  place during the descent loop and each "frame" is a reference to the same
  final array. Copy the state before appending it to the frame list, not
  after the loop finishes.
