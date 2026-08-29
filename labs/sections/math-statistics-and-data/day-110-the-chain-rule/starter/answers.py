"""Exercises 5 to 9 -- forty predictions.

Replace each `None` with the value you think is correct. A `None` is a skip,
not a failure: `pytest starter -q` counts only what you have attempted. When
you are wrong it prints both your answer and the real one, so a wrong guess
is worth more than a blank.

Predict BEFORE you run anything. The two exercises that catch almost everyone
are 7 (where paths meet) and 9 (where a plausible product turns out to be
ten orders of magnitude off), and they only catch you if you commit first.

Every answer is either an exact number, an integer, or a Python bool.
"""

ANSWERS: dict[str, object] = {
    # ----------------------------------------------------------------------
    # Exercise 5 -- rates multiply
    # ----------------------------------------------------------------------
    # 5.1 Gear A turns 2x per turn of B; B turns 3x per turn of C.
    #     How many times does A turn per turn of C?
    "gears_two_stage": None,
    # 5.2 A four-stage train with ratios 2, 3, 1.5, 4. Overall ratio?
    "gears_four_stage": None,
    # 5.3 What does `product([])` return -- the empty product?
    "empty_product": None,
    # 5.4 Does reversing the order of the gear stages change the overall
    #     ratio? True or False.
    "gear_order_matters": None,
    # ----------------------------------------------------------------------
    # Exercise 6 -- composition and the one-variable chain rule
    # ----------------------------------------------------------------------
    # 6.1 f(u) = u squared, g(x) = 3x + 1. What is f(g(2))?
    "composed_value_at_two": None,
    # 6.2 And g(f(2)) -- the other order?
    "composed_other_order_at_two": None,
    # 6.3 d/dx of (3x + 1) squared at x = 2, done correctly.
    "chain_rule_at_two": None,
    # 6.4 The same calculation with the outer derivative wrongly evaluated at
    #     x instead of at u. What number does that mistake produce?
    "chain_rule_mistake_at_two": None,
    # 6.5 The slope of the sigmoid 1/(1 + e**-x) at x = 0.
    "sigmoid_slope_at_zero": None,
    # 6.6 Is that value the sigmoid's LARGEST slope anywhere? True or False.
    "sigmoid_slope_is_maximum": None,
    # 6.7 d/dx of tanh(2x + 1) at x = -0.5. (The inner function is 0 there,
    #     and tanh has slope exactly 1 at 0.)
    "tanh_of_line_slope": None,
    # ----------------------------------------------------------------------
    # Exercise 7 -- depth, and the sum over paths
    # ----------------------------------------------------------------------
    # 7.1 The five stages from dataset.py, starting at x = 1. How many
    #     numbers does `chain_values` return?
    "five_chain_value_count": None,
    # 7.2 The third of the five local rates (the `square` stage). Careful:
    #     it is 2u, and u is the value ARRIVING at that stage.
    "five_chain_third_rate": None,
    # 7.3 The product of all five local rates.
    "five_chain_derivative": None,
    # 7.4 The five stages collapse to ln(2x + 3). Its derivative at x = 1?
    "five_chain_closed_form_derivative": None,
    # 7.5 In `running_products`, what is the LAST entry equal to?
    #     Give the number for the five-stage chain.
    "running_products_last": None,
    # 7.6 Now the two-path graph: u = x squared, v = 3x, f = u x v, at x = 2.
    #     The contribution through the u path.
    "two_path_u_contribution": None,
    # 7.7 The contribution through the v path.
    "two_path_v_contribution": None,
    # 7.8 The correct df/dx. (Not one of the two above, and not their
    #     product.)
    "two_path_total": None,
    # 7.9 The same function written directly is f = 3x cubed. Its derivative
    #     at x = 2 by the power rule?
    "two_path_closed_form": None,
    # 7.10 z = u squared + v squared, u = st, v = s - t, at (s, t) = (2, 3).
    #      What is z?
    "surface_value": None,
    # 7.11 dz/ds at that point. Two paths again: through u and through v.
    "surface_dz_ds": None,
    # 7.12 dz/dt at that point.
    "surface_dz_dt": None,
    # ----------------------------------------------------------------------
    # Exercise 8 -- the engine, and the network
    # ----------------------------------------------------------------------
    # 8.1 x = Value(3.0); y = x + x; y.backward(). What is x.grad?
    "engine_x_plus_x_grad": None,
    # 8.2 x = Value(3.0); y = x * x; y.backward(). What is x.grad?
    "engine_x_times_x_grad": None,
    # 8.3 x = Value(2.0); y = x * x * x; y.backward(). What is x.grad?
    "engine_x_cubed_grad": None,
    # 8.4 What is the gradient of tanh at 0, exactly?
    "tanh_slope_at_zero": None,
    # 8.5 tanh at half the natural logarithm of 3 -- exactly.
    "tanh_at_half_ln_three": None,
    # 8.6 And its slope there -- exactly.
    "tanh_slope_at_half_ln_three": None,
    # 8.7 The network's forward pass: the value of the loss.
    "network_loss": None,
    # 8.8 d loss / d out.
    "network_d_out": None,
    # 8.9 d loss / d vA. Look at what vA multiplies before you answer.
    "network_d_vA": None,
    # 8.10 d loss / d b_pre. (d loss/d b is 9.0, and tanh's slope there
    #      is 0.75.)
    "network_d_b_pre": None,
    # 8.11 d loss / d wB2.
    "network_d_wB2": None,
    # 8.12 d loss / d x1. This one is a SUM over two paths.
    "network_d_x1": None,
    # ----------------------------------------------------------------------
    # Exercise 9 -- cost, collapse, and one honest surprise
    # ----------------------------------------------------------------------
    # 9.1 Reverse mode on a function of 25 inputs and 1 output. How many
    #     forward-and-backward passes to get ALL 25 gradients?
    "reverse_passes_for_25_inputs": None,
    # 9.2 Forward mode, same function. How many passes?
    "forward_passes_for_25_inputs": None,
    # 9.3 Central differences, same function. How many evaluations?
    "numeric_passes_for_25_inputs": None,
    # 9.4 order_of_magnitude(0.9 ** 50) -- the exponent, not the digits.
    "decay_order": None,
    # 9.5 order_of_magnitude(1.1 ** 50).
    "growth_order": None,
    # 9.6 0.5 ** 50 is about 8.88e-16, and float64's epsilon is about
    #     2.22e-16. Does `1.0 + 0.5**50 == 1.0`? True or False.
    #     Think before you answer; the obvious guess is wrong.
    "half_to_the_fiftieth_vanishes": None,
    # 9.7 0.25 is the sigmoid's largest slope. Does `1.0 + 0.25**50 == 1.0`?
    "quarter_to_the_fiftieth_vanishes": None,
}
