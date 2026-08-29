"""Matrix multiplication IS composition — and that is why the rule is the rule.

Run from inside this directory:

    ../.venv/bin/python3 02_composition.py

Two transformations of the plane, applied in both orders, with real coordinates
at every step. Then the three algebraic facts that follow: multiplication is
not commutative, it is associative, and it distributes over addition.
"""

import numpy as np

from dataset import (
    FLIP_AFTER_ROT,
    FLIP_AFTER_ROT_V,
    FLIP_V,
    FLIP_X,
    P,
    P_AT_Q,
    Q,
    Q_AT_P,
    ROT90,
    ROT_AFTER_FLIP,
    ROT_AFTER_FLIP_V,
    ROT_V,
    V,
)
from matmul import chain_costs, matmul_loops, matvec, multiplication_count


def show(M):
    return "[" + ", ".join("[" + ", ".join(f"{v:g}" for v in row) + "]" for row in M) + "]"


A = ROT90  # a quarter turn anticlockwise
B = FLIP_X  # a reflection in the horizontal axis

print("=" * 74)
print("1. Two transformations, read off their columns")
print("=" * 74)
print(f"  A = {show(A)}   a quarter turn anticlockwise")
print(f"  B = {show(B)}   a reflection in the horizontal axis")
print()
print("  How to read a transformation matrix without doing any arithmetic:")
print("  its columns are where the basis vectors land.")
print(f"      A sends (1, 0) to {matvec(A, [1, 0])}  <- A's first column")
print(f"      A sends (0, 1) to {matvec(A, [0, 1])}  <- A's second column")
print(f"      B sends (1, 0) to {matvec(B, [1, 0])}  <- B's first column")
print(f"      B sends (0, 1) to {matvec(B, [0, 1])}  <- B's second column")
assert matvec(A, [1, 0]) == [0, 1]
assert matvec(A, [0, 1]) == [-1, 0]
assert matvec(B, [1, 0]) == [1, 0]
assert matvec(B, [0, 1]) == [0, -1]
print("  That is not a coincidence and it is not a mnemonic. A @ v is a weighted")
print("  sum of A's columns, so A @ (1, 0) takes one copy of column 0 and none")
print("  of column 1. The columns ARE the images of the basis vectors.")

print()
print("=" * 74)
print("2. Doing B and then A, one step at a time")
print("=" * 74)
print(f"  Start at v = {V}.")
step1 = matvec(B, V)
step2 = matvec(A, step1)
print(f"      B @ v          = {step1}      (reflected: y flipped sign)")
print(f"      A @ (B @ v)    = {step2}      (then turned a quarter anticlockwise)")
assert step1 == FLIP_V
assert step2 == ROT_AFTER_FLIP_V

print()
print("  Now the single matrix that does both in one step:")
AB = matmul_loops(A, B)
print(f"      A @ B          = {show(AB)}")
print(f"      (A @ B) @ v    = {matvec(AB, V)}")
assert AB == ROT_AFTER_FLIP
assert matvec(AB, V) == step2
print("  Same destination, one multiplication instead of two.")
print("  A @ B is the reflection in the line y = x: it swaps the coordinates,")
print(f"  and {V} becoming {matvec(AB, V)} is exactly that.")
print()
print("  Read the order carefully, because it is the thing people get wrong:")
print("  in A @ B, B runs FIRST. It is the one standing next to the vector in")
print("  A @ (B @ v). Matrices compose right to left, like nested function")
print("  calls: A(B(v)). English says 'A times B'; the arithmetic says 'B, then A'.")

print()
print("=" * 74)
print("3. The same two operations in the other order")
print("=" * 74)
other1 = matvec(A, V)
other2 = matvec(B, other1)
print(f"      A @ v          = {other1}     (turned first)")
print(f"      B @ (A @ v)    = {other2}    (then reflected)")
BA = matmul_loops(B, A)
print(f"      B @ A          = {show(BA)}")
print(f"      (B @ A) @ v    = {matvec(BA, V)}")
assert other1 == ROT_V
assert other2 == FLIP_AFTER_ROT_V
assert BA == FLIP_AFTER_ROT
assert matvec(BA, V) == other2

print()
print(f"  A @ B = {show(AB)}   reflection in the line y = x")
print(f"  B @ A = {show(BA)}   reflection in the line y = -x")
print(f"  The same starting point {V} ends at {matvec(AB, V)} one way and "
      f"{matvec(BA, V)} the other.")
assert AB != BA
assert matvec(AB, V) != matvec(BA, V)
print()
print("  Matrix multiplication is NOT commutative. That is not a defect and it")
print("  is not a subtlety: it is the honest consequence of what it means.")
print("  Putting your socks on and then your shoes is not the same as putting")
print("  your shoes on and then your socks, and no amount of algebra will make")
print("  it so.")
print()
print("  NumPy, on the same numbers, to be sure the from-scratch code is right:")
npA, npB = np.array(A), np.array(B)
print(f"      npA @ npB = {(npA @ npB).tolist()}")
print(f"      npB @ npA = {(npB @ npA).tolist()}")
assert (npA @ npB).tolist() == AB
assert (npB @ npA).tolist() == BA

print()
print("=" * 74)
print("4. A second pair, where neither answer is a tidy reflection")
print("=" * 74)
PQ = matmul_loops(P, Q)
QP = matmul_loops(Q, P)
elementwise = [[P[i][j] * Q[i][j] for j in range(2)] for i in range(2)]
print(f"  P = {show(P)}    Q = {show(Q)}")
print(f"      P @ Q = {show(PQ)}     1*5 + 2*7 = 19, and so on")
print(f"      Q @ P = {show(QP)}     5*1 + 6*3 = 23, and so on")
print(f"      P * Q = {show(elementwise)}      no summing anywhere; section 5 of")
print("                                       03_star_versus_at.py is about this")
assert PQ == P_AT_Q
assert QP == Q_AT_P
assert PQ != QP != elementwise
print("  Two matrices, three different answers, and only one of them is what")
print("  'multiply these matrices' means in linear algebra.")

print()
print("=" * 74)
print("5. What IS true: associativity")
print("=" * 74)
C = [[1, 1], [0, 2]]
left_first = matmul_loops(matmul_loops(A, B), C)
right_first = matmul_loops(A, matmul_loops(B, C))
print(f"  C = {show(C)}")
print(f"      (A @ B) @ C = {show(left_first)}")
print(f"      A @ (B @ C) = {show(right_first)}")
assert left_first == right_first
print("  Identical. The BRACKETS may move freely; the ORDER may not. Those are")
print("  two different statements and confusing them is the usual mistake.")
print()
print("  Associativity is not a curiosity. It is the only reason you are allowed")
print("  to choose the cheaper way to evaluate a chain, and the choice is worth")
print("  a great deal:")
for label, (m, n, p, q) in [
    ("(10, 100) @ (100, 5) @ (5, 50)", (10, 100, 5, 50)),
    ("(1024, 4096) @ (4096, 8) @ (8, 4096)", (1024, 4096, 8, 4096)),
]:
    left_first, right_first = chain_costs(m, n, p, q)
    ratio = right_first / left_first
    print(f"      {label}")
    print(f"        (AB)C : {left_first:>15,} multiplications")
    print(f"        A(BC) : {right_first:>15,} multiplications   ({ratio:.0f}x more)")
assert chain_costs(10, 100, 5, 50) == (7_500, 75_000)
assert chain_costs(1024, 4096, 8, 4096) == (67_108_864, 17_314_086_912)
assert 17_314_086_912 // 67_108_864 == 258
print("  Same answer to the last digit, 258 times the arithmetic. The second")
print("  set of shapes is a low-rank adapter on a 4096-wide layer, which is a")
print("  real thing people train, and this cost gap is most of why they can.")

print()
print("=" * 74)
print("6. What IS true: distributivity")
print("=" * 74)
D = [[2, 0], [1, 1]]
sum_then_mult = matmul_loops(A, [[B[i][j] + D[i][j] for j in range(2)] for i in range(2)])
mult_then_sum_parts = (matmul_loops(A, B), matmul_loops(A, D))
mult_then_sum = [
    [mult_then_sum_parts[0][i][j] + mult_then_sum_parts[1][i][j] for j in range(2)]
    for i in range(2)
]
print(f"  D = {show(D)}")
print(f"      A @ (B + D)     = {show(sum_then_mult)}")
print(f"      A @ B  +  A @ D = {show(mult_then_sum)}")
assert sum_then_mult == mult_then_sum
print("  Equal. This is what lets you split a layer's weights into a base part")
print("  and a small correction and add the two results — the other half of why")
print("  adapters work.")

print()
print("=" * 74)
print("7. The cost of the chain, counted rather than asserted")
print("=" * 74)
print("  (m, n) @ (n, p) runs its innermost line m*n*p times, once per")
print("  (row, column, inner step). Nothing about that count is an estimate:")
for m, n, p in [(2, 3, 2), (10, 100, 5), (200, 200, 200)]:
    label = f"({m}, {n}) @ ({n}, {p})"
    print(f"      {label:<26} {multiplication_count(m, n, p):>11,} multiplications")
assert multiplication_count(200, 200, 200) == 8_000_000
print("  Eight million for a pair of 200 by 200 matrices, which is small by any")
print("  modern standard. 05_cost_and_speed.py times that one for real.")

print()
print("02_composition.py: every assertion held.")
