"""Exercises 2 to 7 -- your predictions. Work them out BEFORE running anything.

Almost all of these can be done on paper or in your head. That is deliberate: a
lab about derivatives whose answers you cannot check by hand is a lab that
teaches you to trust output.

Replace each `None` with your answer. Anything still `None` is SKIPPED by the
test suite rather than failed, so your score only ever counts work you actually
attempted.

Check yourself from the LAB DIRECTORY:

    .venv/bin/pytest starter -q
"""

# =============================================================================
# Exercise 2 -- average rates, before any calculus
# =============================================================================

# 2.1 A car's distance from a post is 4 * t**2 metres at t seconds. What is its
#     average speed, in metres per second, over the whole interval from t = 0
#     to t = 6? A float.
AVERAGE_SPEED_WHOLE_TRIP = None

# 2.2 What is its average speed over the fourth second alone, from t = 3 to
#     t = 4? A float.
AVERAGE_SPEED_FOURTH_SECOND = None

# 2.3 The car was never actually travelling at exactly the answer to 2.1 for
#     the whole trip. What does that average speed describe?
#     One of these strings:
#       "the speed shown on the speedometer at t = 3"
#       "the constant speed that would have covered the same distance in the
#        same time"
#       "the highest speed the car reached"
AVERAGE_SPEED_MEANING = None

# 2.4 What does `average_rate(f, 3.0, 3.0)` do in this lab? Answer with the
#     EXCEPTION CLASS itself, not a string. For example: ValueError
ZERO_WIDTH_RAISES = None

# 2.5 For f(x) = x**2, the average rate over [3, 3 + h] simplifies to a very
#     short expression in h. Which one?
#     One of these strings:  "6", "6 + h", "6 + h**2", "9 + 6h"
SIMPLIFIED_SECANT_SLOPE = None


# =============================================================================
# Exercise 3 -- the shrinking interval and the limit
# =============================================================================

# 3.1 Using your answer to 2.5, what are the four secant slopes for
#     h = 1, 0.1, 0.01 and 0.001? A list of four floats.
SETTLING_SEQUENCE = None

# 3.2 What number does that sequence settle on? A float.
SETTLED_VALUE = None

# 3.3 For f(x) = x**2 at x = 3, do the secant slopes approach 6 from ABOVE or
#     from BELOW as h shrinks through positive values?
#     One of these strings: "above", "below"
APPROACH_DIRECTION = None

# 3.4 The tangent line to y = x**2 at x = 3 passes through (3, 9) with the
#     derivative as its slope. Give (slope, intercept) as a tuple of two
#     floats, for the line written as y = slope * x + intercept.
TANGENT_LINE = None

# 3.5 Which statement about a tangent line is correct?
#     One of these strings:
#       "a tangent line touches the curve at exactly one point"
#       "a tangent line is the line the secant lines approach as the interval
#        shrinks"
#       "a tangent line never crosses the curve"
TANGENT_DEFINITION = None


# =============================================================================
# Exercise 4 -- the rules
# =============================================================================

# 4.1 d/dx of 7, at any x. A float.
DERIVATIVE_OF_SEVEN = None

# 4.2 d/dx of x**5, evaluated at x = 1.5. A float. (Power rule: n * x**(n-1).)
DERIVATIVE_OF_X5_AT_1_5 = None

# 4.3 d/dx of 5 * x**2, evaluated at x = 3. A float.
DERIVATIVE_OF_5X2_AT_3 = None

# 4.4 d/dx of x**2 + x**3, evaluated at x = 2. A float.
DERIVATIVE_OF_SUM_AT_2 = None

# 4.5 d/dx of ln(x), evaluated at x = 4. A float.
DERIVATIVE_OF_LN_AT_4 = None

# 4.6 The slope of b**x at x = 0, for b = 2, is not 1. What number is it?
#     One of these strings:
#       "1, the same for every base"
#       "the natural logarithm of 2, about 0.693"
#       "2, the base itself"
SLOPE_OF_2X_AT_ZERO = None

# 4.7 What makes e special among all the possible bases?
#     One of these strings:
#       "e**x is the only function whose graph is a straight line"
#       "e is the base for which the slope at x = 0 is exactly 1, so e**x is
#        its own derivative"
#       "e is the largest base for which the derivative exists"
WHY_E_IS_SPECIAL = None


# =============================================================================
# Exercise 5 -- forward against central
# =============================================================================

# 5.1 For f(x) = x**2 at x = 3, the forward difference at step h is exactly
#     6 + h. What is the backward difference at the same h?
#     One of these strings: "6 + h", "6 - h", "6", "6 + h**2"
BACKWARD_ON_A_PARABOLA = None

# 5.2 What is the central difference for that same function at that same point,
#     for ANY h at all? A float.
CENTRAL_ON_A_PARABOLA = None

# 5.3 If you divide h by 10, roughly what happens to the FORWARD difference's
#     truncation error?
#     One of these strings: "divided by 10", "divided by 100", "unchanged"
FORWARD_ERROR_SCALING = None

# 5.4 And to the CENTRAL difference's truncation error?
#     One of these strings: "divided by 10", "divided by 100", "unchanged"
CENTRAL_ERROR_SCALING = None

# 5.5 How many calls to f does the central difference need, per estimate?
#     An integer.
CENTRAL_FUNCTION_CALLS = None

# 5.6 The central difference is the average of which two rules?
#     One of these strings:
#       "the forward and backward differences"
#       "the forward difference at h and at 2h"
#       "the first and second differences"
CENTRAL_IS_THE_AVERAGE_OF = None


# =============================================================================
# Exercise 6 -- the U-shaped error curve
# =============================================================================

# 6.1 As h shrinks from 1e-1 towards 1e-14, what does the TRUNCATION error do?
#     One of these strings: "shrinks", "grows", "stays the same"
TRUNCATION_AS_H_SHRINKS = None

# 6.2 And what does the ROUNDING error do?
#     One of these strings: "shrinks", "grows", "stays the same"
#     Note the answer is not the same as 6.1; if it were, there would be no U.
ROUNDING_AS_H_SHRINKS = None

# 6.3 What is `forward_difference(math.exp, 1.0, 1e-300)`? A float, and it is
#     not close to e. Think about what exp(1 + 1e-300) is stored as.
ABSURDLY_SMALL_H_RESULT = None

# 6.4 Why is that the answer?
#     One of these strings:
#       "Python cannot represent 1e-300"
#       "exp(1 + 1e-300) and exp(1) are the same float64, so their difference
#        is exactly zero"
#       "the exponential function is flat near x = 1"
ABSURDLY_SMALL_H_REASON = None

# 6.5 Roughly where does the CENTRAL difference's error bottom out for float64?
#     One of these strings: "around 1e-2", "around 1e-6", "around 1e-16"
BEST_CENTRAL_H_BAND = None

# 6.6 And the FORWARD difference's?
#     One of these strings: "around 1e-2", "around 1e-8", "around 1e-16"
BEST_FORWARD_H_BAND = None

# 6.7 True or false: choosing h = 1e-12 for a central difference is a more
#     careful choice than h = 1e-5. A bool.
TINY_H_IS_MORE_CAREFUL = None


# =============================================================================
# Exercise 7 -- flat points, curvature, and corners
# =============================================================================

# 7.1 f(x) = x**3 - 3x has a zero derivative at x = -1 and at x = +1. Which is
#     the MAXIMUM?
#     One of these strings: "x = -1", "x = +1", "both", "neither"
WHICH_IS_THE_MAXIMUM = None

# 7.2 What is f''(x) for that cubic at x = +1? A float. (f'' of x**3 - 3x is
#     6x, so this is one multiplication.)
SECOND_DERIVATIVE_AT_PLUS_ONE = None

# 7.3 f(x) = x**3 at x = 0 has f'(0) = 0 and f''(0) = 0. What kind of point is
#     it?
#     One of these strings: "minimum", "maximum", "neither"
CUBE_AT_ZERO = None

# 7.4 What does `classify_stationary_point` return there?
#     One of these strings: "minimum", "maximum", "undecided", "not stationary"
CUBE_AT_ZERO_CLASSIFICATION = None

# 7.5 What does a zero first derivative tell you, on its own?
#     One of these strings:
#       "that you are at a minimum"
#       "that the function is flat there, and nothing more"
#       "that the function is constant"
WHAT_ZERO_DERIVATIVE_MEANS = None

# 7.6 f(x) = |x| at x = 0. What does the FORWARD difference return? A float.
ABS_FORWARD_AT_ZERO = None

# 7.7 What does the BACKWARD difference return there? A float.
ABS_BACKWARD_AT_ZERO = None

# 7.8 What does the CENTRAL difference return there? A float.
ABS_CENTRAL_AT_ZERO = None

# 7.9 Does |x| have a derivative at 0? A bool.
ABS_IS_DIFFERENTIABLE_AT_ZERO = None

# 7.10 What does the central difference of max(x, 0) return at x = 0? A float.
RELU_CENTRAL_AT_ZERO = None

# 7.11 The cheapest way to detect that you are standing on a corner, using
#      values you have already computed:
#      One of these strings:
#        "check whether the central difference is zero"
#        "check whether the forward and backward differences disagree"
#        "check whether the function returns nan"
HOW_TO_DETECT_A_CORNER = None

# 7.12 Why does any of this matter for training a model?
#      One of these strings:
#        "the derivative tells you which way to move to make the loss smaller"
#        "the derivative tells you what the loss will be"
#        "the derivative tells you how many layers the network needs"
WHY_DERIVATIVES_MATTER_FOR_AI = None
