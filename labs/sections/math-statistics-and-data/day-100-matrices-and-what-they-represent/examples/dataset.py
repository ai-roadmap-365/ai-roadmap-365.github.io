"""The one small dataset this lab reads three different ways.

INVENTED DATA. Fenwick Road Garden Centre does not exist, and neither do
these recipes or these prices. The numbers were chosen so that every result
in this lab can be checked by hand on paper in under a minute, which is the
only property that matters for a teaching example.

Three potting mixes, four ingredients, litres of each ingredient per bag:

                base   bark   grit   compost
    Seedling       2      4      1         3
    Container      0      5      2         7
    Alpine         6      1      4         2

and the ingredient prices, in pence per litre:

    base 10, bark 2, grit 5, compost 1

Everything else in the lab is derived from those two blocks of numbers.
"""

MIX_NAMES = ["Seedling", "Container", "Alpine"]
INGREDIENT_NAMES = ["base", "bark", "grit", "compost"]

# The recipes, as a plain nested list: one inner list per mix.
RECIPES = [
    [2, 4, 1, 3],
    [0, 5, 2, 7],
    [6, 1, 4, 2],
]

# Pence per litre, one entry per ingredient, in the same column order.
PRICE_PER_LITRE = [10, 2, 5, 1]

# The answers, worked out by hand, so the code has something to be checked
# against rather than merely something to print.
#
#   Seedling : 2*10 + 4*2 + 1*5 + 3*1 = 20 +  8 +  5 + 3 = 36
#   Container: 0*10 + 5*2 + 2*5 + 7*1 =  0 + 10 + 10 + 7 = 27
#   Alpine   : 6*10 + 1*2 + 4*5 + 2*1 = 60 +  2 + 20 + 2 = 84
COST_PER_BAG_PENCE = [36, 27, 84]

# Row sums: how many litres are in each bag.
LITRES_PER_BAG = [10, 14, 13]

# Column sums: how many litres of each ingredient one bag of every mix needs.
LITRES_PER_INGREDIENT = [8, 10, 7, 12]
