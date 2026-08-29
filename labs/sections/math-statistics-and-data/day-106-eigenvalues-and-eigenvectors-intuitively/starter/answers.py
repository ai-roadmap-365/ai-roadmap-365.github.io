"""Exercises 2 to 5 — predictions. Work them out, then let the tests check you.

Every answer below is `None`, which makes its test SKIP. Replace a None with
your answer and the skip becomes a pass or a failure — and a failure prints
both your answer and the real one, so a wrong guess still teaches you
something.

The rule for this file: PREDICT FIRST, then run. Every one of these can be
reasoned out from the lesson. Looking them up by running NumPy first turns a
thinking exercise into a typing exercise.
"""

# ==========================================================================
# EXERCISE 2 — solving the 2x2 by hand
#
#     A = [[4, 1],
#          [2, 3]]
# ==========================================================================

#: 2a. The trace of A (the sum of the diagonal entries). An integer.
TRACE_OF_A = None

#: 2b. The determinant of A. An integer.
DETERMINANT_OF_A = None

#: 2c. The characteristic equation is lambda^2 - b*lambda + c = 0.
#:     Give (b, c) as a tuple of two integers.
CHARACTERISTIC_COEFFICIENTS = None

#: 2d. The discriminant, b^2 - 4c. An integer.
#:     Its SIGN is the interesting part: positive means two real eigenvalues,
#:     zero means one repeated, negative means none that are real.
DISCRIMINANT = None

#: 2e. The two eigenvalues, as a tuple of two integers, LARGEST FIRST.
EIGENVALUES_LARGEST_FIRST = None

#: 2f. An eigenvector for the LARGER eigenvalue, as a tuple of two integers
#:     with no common factor. There are infinitely many correct answers that
#:     differ by scale and sign; the test compares directions, so any
#:     non-zero multiple of the right one passes.
#:     Hint: solve (A - 5I) v = 0. The first row of A - 5I is [-1, 1].
EIGENVECTOR_FOR_LARGER = None

#: 2g. An eigenvector for the SMALLER eigenvalue, same rules.
#:     Hint: the first row of A - 2I is [2, 1].
EIGENVECTOR_FOR_SMALLER = None


# ==========================================================================
# EXERCISE 3 — the standard transformations
# ==========================================================================

#: 3a. How many DISTINCT eigen-lines does the shear [[1, 1], [0, 1]] have?
#:     An integer. Count lines, not columns returned by NumPy — those are not
#:     the same number here, and the difference is the point of the question.
SHEAR_EIGEN_LINE_COUNT = None

#: 3b. Are the eigenvalues of the 90-degree rotation [[0, -1], [1, 0]] real?
#:     True or False. Picture what a rotation does to an arrow before you
#:     reach for the algebra.
ROTATION_EIGENVALUES_ARE_REAL = None

#: 3c. The MAGNITUDE (absolute value) of each eigenvalue of that rotation.
#:     A single number, since both are the same. Hint: a rotation changes no
#:     lengths at all.
ROTATION_EIGENVALUE_MAGNITUDE = None

#: 3d. numpy.linalg.eig is given the real matrix A, whose eigenvalues are 5
#:     and 2 — both real. What dtype does it return the eigenvalues in?
#:     The string 'float64' or the string 'complex128'.
#:     Predict from the documentation, then run it. If your prediction and the
#:     machine disagree, the machine is right and that disagreement is one of
#:     the things this lab exists to show you.
EIG_DTYPE_ON_A = None

#: 3e. The determinant of the projection [[1, 0], [0, 0]], and the smaller of
#:     its two eigenvalues, as a tuple of two numbers.
#:     They are the same number, and that is not a coincidence.
PROJECTION_DET_AND_SMALLEST_EIGENVALUE = None

#: 3f. The eigenvalues of the reflection [[1, 0], [0, -1]], as a tuple of two
#:     integers, largest first. One of them is negative — say what a negative
#:     eigenvalue means to yourself before you write it down.
REFLECTION_EIGENVALUES = None

#: 3g. For a symmetric matrix, at what angle (in degrees) do the eigenvectors
#:     meet? A single number.
SYMMETRIC_EIGENVECTOR_ANGLE_DEG = None


# ==========================================================================
# EXERCISE 4 — the power method on A, started from a seeded random vector
# ==========================================================================

#: 4a. Which eigenvalue does the power method converge towards? A number.
POWER_METHOD_FINDS_EIGENVALUE = None

#: 4b. The direction it converges to, in degrees in [0, 180). A number.
#:     Hint: it is the direction of the eigenvector for 4a.
POWER_METHOD_FINDS_DIRECTION_DEG = None

#: 4c. Each iteration, the remaining error shrinks by roughly a constant
#:     factor. What factor? A number between 0 and 1.
#:     Hint: it is a ratio of the two eigenvalues, and the smaller one is on
#:     top. Reason about which ingredient is dying out relative to which.
CONVERGENCE_RATIO = None

#: 4d. If the two eigenvalues were 5 and 4.9 instead of 5 and 2, would the
#:     power method need MORE or FEWER iterations to reach the same
#:     tolerance? The string 'more' or the string 'fewer'.
CLOSE_EIGENVALUES_NEED = None

#: 4e. If you never normalise, what does the length of A^k v0 do as k grows
#:     past a few hundred? One of the strings 'overflows to inf',
#:     'shrinks to zero', 'stays at 1'.
UNNORMALISED_LENGTH_BEHAVIOUR = None


# ==========================================================================
# EXERCISE 5 — PCA on the invented cloud
#
# The cloud is 400 points, deliberately stretched along 30 degrees, with a
# standard deviation of 3.0 along that direction and 0.4 across it, centred
# at (5, -2).
# ==========================================================================

#: 5a. What is the shape of the covariance matrix of a (400, 2) dataset?
#:     A tuple. It is NOT (400, 400) and it is NOT (400, 2).
COVARIANCE_SHAPE = None

#: 5b. Is the covariance matrix symmetric? True or False.
COVARIANCE_IS_SYMMETRIC = None

#: 5c. Roughly what direction, in degrees, does the top eigenvector point
#:     along? A number. The test allows one degree of slack, because 400
#:     samples estimate a direction rather than reproduce it.
TOP_COMPONENT_DIRECTION_DEG = None

#: 5d. The square root of the LARGEST eigenvalue should come out close to one
#:     of the numbers the cloud was built with. Which one? A number.
#:     Half a unit of slack is allowed.
SQRT_OF_TOP_EIGENVALUE = None

#: 5e. Which NumPy routine is the right one for a covariance matrix?
#:     The string 'eig' or the string 'eigh'.
RIGHT_ROUTINE_FOR_COVARIANCE = None

#: 5f. numpy.allclose is used to compare the top eigenvector against the true
#:     direction (0.866, 0.5) that the cloud was built along. The answer is
#:     correct. Does numpy.allclose return True or False?
#:     Think about what is and is not determined about an eigenvector.
ALLCLOSE_ON_THE_CORRECT_COMPONENT = None

#: 5g. If you forget to subtract the mean before computing the covariance,
#:     is the top eigenvector still within 5 degrees of the truth?
#:     True or False.
UNCENTRED_STILL_CORRECT = None
