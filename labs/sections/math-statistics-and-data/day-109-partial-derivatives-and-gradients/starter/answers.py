"""Exercises 2 to 8 -- your predictions. Work them out BEFORE running anything.

Almost every one of these can be done on paper. That is deliberate: a lab about
derivatives whose answers you cannot check by hand is a lab that teaches you to
trust output.

Replace each `None` with your answer. Anything still `None` is SKIPPED by the
test suite rather than failed, so your score only ever counts work you actually
attempted.

Check yourself from the LAB DIRECTORY:

    .venv/bin/pytest starter -q

Throughout, these are the six surfaces from `surfaces.py`:

    bowl     f = x^2 + 3y^2
    plane    f = 3x - 2y + 5
    product  f = xy
    saddle   f = x^2 - y^2
    dome     f = -(x^2 + y^2)
    cubic    f = x^3 + x*y^2
"""

# =============================================================================
# Exercise 2 -- partial derivatives by hand
# =============================================================================

# 2.1 f = x^2 + 3y^2. What is df/dx at the point (2, 1)? A float.
#     Freeze y at 1, differentiate x^2 + 3 with respect to x, put x = 2.
BOWL_DF_DX_AT_2_1 = None

# 2.2 The same function and the same point. What is df/dy? A float.
BOWL_DF_DY_AT_2_1 = None

# 2.3 f = xy. What is df/dx at (1, 0)? A float.
#     Careful: this is the one that catches people.
PRODUCT_DF_DX_AT_1_0 = None

# 2.4 f = xy at the same point (1, 0). What is df/dy? A float.
PRODUCT_DF_DY_AT_1_0 = None

# 2.5 Given your answers to 2.3 and 2.4: is the surface flat at (1, 0)?
#     Answer "yes" or "no".
IS_THE_PRODUCT_FLAT_AT_1_0 = None

# 2.6 f = x^3 + x*y^2. What is df/dx at (2, 1)? An integer or a float.
#     df/dx = 3x^2 + y^2. Substitute.
CUBIC_DF_DX_AT_2_1 = None

# 2.7 Same function, same point. What is df/dy? df/dy = 2xy.
CUBIC_DF_DY_AT_2_1 = None

# 2.8 Why is the symbol written with a rounded d rather than a straight one?
#     Answer with one of these strings:
#       "it is a different kind of derivative with different rules"
#       "it signals that the function has other inputs being held fixed"
#       "it means the answer is approximate rather than exact"
WHY_THE_ROUNDED_D = None


# =============================================================================
# Exercise 3 -- the gradient as a vector
# =============================================================================

# 3.1 The gradient of the bowl at (2, 1), as a list of two floats.
#     This is just 2.1 and 2.2 side by side.
BOWL_GRADIENT_AT_2_1 = None

# 3.2 How many components does the gradient of f(x, y) = x^2 + 3y^2 have?
#     An integer. The graph of this function is a surface in three dimensions;
#     the question is about the gradient, not the graph.
BOWL_GRADIENT_LENGTH = None

# 3.3 The gradient of the plane 3x - 2y + 5 at (100, -100), as a list of two
#     floats. Think before you compute anything.
PLANE_GRADIENT_FAR_AWAY = None

# 3.4 |grad f| for the bowl at (1, 1), where the gradient is (2, 6).
#     A float. This is Day 99's norm: sqrt(2^2 + 6^2).
BOWL_GRADIENT_MAGNITUDE_AT_1_1 = None

# 3.5 What does that magnitude MEAN, in words?
#     Answer with one of these strings:
#       "the height of the surface at that point"
#       "the rate of climb in the steepest direction, per unit of distance"
#       "the distance from the point to the minimum"
WHAT_THE_MAGNITUDE_MEANS = None

# 3.6 A model has 500 parameters. How many numbers are in the gradient of its
#     loss? An integer.
GRADIENT_LENGTH_FOR_500_PARAMETERS = None


# =============================================================================
# Exercise 4 -- directional derivatives and steepest ascent
# =============================================================================

# 4.1 At (1, 1) on the bowl the gradient is (2, 6). What is the directional
#     derivative along the direction (1, 0)? A float.
#     Remember that a directional derivative uses the UNIT direction, and
#     (1, 0) already has length 1.
BOWL_RATE_DUE_EAST = None

# 4.2 The same point, along the direction (0, 1). A float.
BOWL_RATE_DUE_NORTH = None

# 4.3 The same point, along the direction (3, -1). A float.
#     Work out the dot product of (2, 6) with (3, -1) first, then think about
#     what dividing by the length of (3, -1) does to a zero.
BOWL_RATE_ALONG_3_MINUS_1 = None

# 4.4 What is the LARGEST directional derivative available at that point, over
#     every possible unit direction? A float, to three decimal places or
#     better. You already computed it in 3.4.
BOWL_LARGEST_POSSIBLE_RATE = None

# 4.5 And the smallest (that is, the most negative)? A float.
BOWL_SMALLEST_POSSIBLE_RATE = None

# 4.6 If you sweep 360 directions one degree apart and take the largest rate,
#     will it exactly equal your answer to 4.4?
#     Answer with one of these strings:
#       "yes, exactly"
#       "no, slightly smaller"
#       "no, slightly larger"
WILL_THE_SWEEP_HIT_THE_MAXIMUM = None

# 4.7 A direction u makes an angle A with the gradient. The directional
#     derivative along u equals |grad f| times WHAT function of A?
#     Answer with one of these strings: "sin", "cos", "tan"
WHICH_TRIG_FUNCTION = None


# =============================================================================
# Exercise 5 -- contours and perpendicularity
# =============================================================================

# 5.1 A contour (or level set) of f is the set of points where f takes one
#     fixed value. On the bowl x^2 + 3y^2, what shape are the contours?
#     Answer with one of these strings: "circles", "ellipses", "straight lines"
BOWL_CONTOUR_SHAPE = None

# 5.2 On the plane 3x - 2y + 5, what shape are the contours?
#     Same three choices.
PLANE_CONTOUR_SHAPE = None

# 5.3 What is the angle, in degrees, between the gradient at a point and the
#     tangent to the contour through that point? A number.
ANGLE_BETWEEN_GRADIENT_AND_CONTOUR = None

# 5.4 If you walk a very short distance ALONG a contour, roughly how much does
#     f change?
#     Answer with one of these strings:
#       "it grows at the rate |grad f|"
#       "essentially nothing, to first order"
#       "it shrinks at the rate |grad f|"
WHAT_HAPPENS_ALONG_A_CONTOUR = None

# 5.5 The lab checks perpendicularity by taking two points a distance delta
#     apart on an exactly parametrised contour and dotting the chord between
#     them with the unit gradient. The answer is not exactly zero. When delta
#     is divided by 10, what happens to the dot product?
#     Answer with one of these strings:
#       "it stays the same"
#       "it is divided by about 10"
#       "it is divided by about 100"
HOW_THE_DOT_PRODUCT_SHRINKS = None

# 5.6 Why does the lab parametrise each contour algebraically instead of
#     finding the contour direction by rotating the gradient 90 degrees?
#     Answer with one of these strings:
#       "rotating is slower to compute"
#       "rotating would make the result true by construction and prove nothing"
#       "rotating only works in two dimensions"
WHY_NOT_ROTATE_THE_GRADIENT = None


# =============================================================================
# Exercise 6 -- step size, and Day 108's U-curve
# =============================================================================

# 6.1 For f = x^2, the central difference ((x+h)^2 - (x-h)^2) / (2h) simplifies
#     to what? Answer with one of these strings: "2x", "2x + h", "2x + h^2"
CENTRAL_DIFFERENCE_ON_A_SQUARE = None

# 6.2 For f = x^3, the same expression simplifies to 3x^2 plus what?
#     Answer with one of these strings: "0", "h", "h^2", "h^3"
CENTRAL_DIFFERENCE_ERROR_ON_A_CUBE = None

# 6.3 On a cubic, if you divide h by 10, the METHOD error is divided by what?
#     An integer.
TRUNCATION_ERROR_IMPROVEMENT_PER_DECADE = None

# 6.4 As h gets very small, a second source of error takes over. What is it?
#     Answer with one of these strings:
#       "the function becomes non-differentiable"
#       "subtracting two nearly equal floats loses the digits they shared"
#       "numpy switches to a lower precision"
WHAT_GOES_WRONG_FOR_TINY_H = None

# 6.5 Which h in the range 1e-1 down to 1e-14 gives the SMALLEST total error
#     for a central difference on the cubic, on float64? A float, such as
#     1e-05. The trough sits near the cube root of machine epsilon.
BEST_H_FOR_CENTRAL = None

# 6.6 And for a FORWARD difference, whose method error shrinks like h rather
#     than h^2, so the trough sits near the square root of machine epsilon?
#     A float.
BEST_H_FOR_FORWARD = None

# 6.7 At h = 1e-14 the central difference on the cubic gives an answer that is
#     compared with the answer at h = 0.1:
#     Answer with one of these strings: "much better", "about the same",
#     "much worse"
CENTRAL_AT_TINY_H_VERSUS_MODERATE_H = None


# =============================================================================
# Exercise 7 -- the zero gradient, and what it does not tell you
# =============================================================================

# 7.1 The gradient of the bowl at the origin, as a list of two floats.
BOWL_GRADIENT_AT_ORIGIN = None

# 7.2 The gradient of the saddle x^2 - y^2 at the origin, as a list of two
#     floats.
SADDLE_GRADIENT_AT_ORIGIN = None

# 7.3 The gradient of the dome -(x^2 + y^2) at the origin, as a list of two
#     floats.
DOME_GRADIENT_AT_ORIGIN = None

# 7.4 Given three identical answers above: can the gradient alone tell you
#     which of the three points is a minimum? Answer "yes" or "no".
CAN_THE_GRADIENT_TELL_THEM_APART = None

# 7.5 What is the general name for a point where every partial derivative is
#     zero? Answer with one of these strings:
#       "minimum", "stationary point", "inflection point"
NAME_FOR_A_ZERO_GRADIENT_POINT = None

# 7.6 Which object would you need in order to tell a minimum from a maximum
#     from a saddle -- the matrix of SECOND partial derivatives?
#     Answer with one of these strings: "Jacobian", "Hessian", "Laplacian"
WHAT_YOU_NEED_INSTEAD = None

# 7.7 On the saddle x^2 - y^2, walking 0.5 due east from the origin changes f
#     by how much? A float, with its sign.
SADDLE_CHANGE_WALKING_EAST = None

# 7.8 And 0.5 due north? A float, with its sign.
SADDLE_CHANGE_WALKING_NORTH = None


# =============================================================================
# Exercise 8 -- models, cost, and the AI thread
# =============================================================================

# 8.1 The loss L = (1/4) sum (w1*a + w2*b + c - y)^2 over the four samples in
#     surfaces.py, evaluated at w1 = w2 = c = 1. A float.
#     The four predictions are 4, 4, 7, 2 against targets 8, 7, 15, 3.
MODEL_LOSS_AT_ONES = None

# 8.2 dL/dw1 at that point. An integer or a float.
#     dL/dw1 = (2/4) sum (residual * a), and the four residuals are
#     -4, -3, -8, -1 with a values 1, 2, 3, 0.
MODEL_DL_DW1 = None

# 8.3 dL/dw2 there. The b values are 2, 1, 3, 1.
MODEL_DL_DW2 = None

# 8.4 dL/dc there. The c term has a coefficient of 1 in every sample.
MODEL_DL_DC = None

# 8.5 How many separate evaluations of the loss does ONE numerical gradient of
#     a 3-parameter model cost, using a central difference? An integer.
EVALUATIONS_FOR_A_3_PARAMETER_GRADIENT = None

# 8.6 And for a model with 1,000,000 parameters? An integer.
EVALUATIONS_FOR_A_MILLION_PARAMETER_GRADIENT = None

# 8.7 Reverse-mode automatic differentiation gets the whole gradient for a cost
#     that does what as the parameter count grows?
#     Answer with one of these strings:
#       "grows in proportion to the number of parameters"
#       "stays roughly one forward pass plus one backward pass"
#       "grows as the square of the number of parameters"
COST_OF_REVERSE_MODE_AUTODIFF = None

# 8.8 Numerical differentiation is still genuinely useful in training code, for
#     one specific job. Which?
#     Answer with one of these strings:
#       "it is faster than autodiff for small models"
#       "checking that a hand-written backward pass is correct"
#       "it handles non-differentiable functions that autodiff cannot"
WHAT_NUMERICAL_GRADIENTS_ARE_STILL_FOR = None

# 8.9 To make a loss go DOWN, you step along which vector?
#     Answer with one of these strings:
#       "the gradient"
#       "the negative gradient"
#       "any direction perpendicular to the gradient"
WHICH_WAY_TO_STEP_TO_REDUCE_A_LOSS = None
