# Where did the West's revenue go?

**Question.** Four regions sell through two channels. Did any region's revenue trajectory change around the month-13 pricing change, and is the change big enough and clean enough to act on?

**Decision this feeds.** Whether to roll the month-13 pricing change back in the West before it is extended to the other three regions.

## Conclusion

1. 8 of 192 rows (4.2%) have no revenue, and 100% of those gaps are partner rows -- the missingness is a channel problem, not random loss (Figure 1)
2. Revenue is two populations rather than one: the median partner region-month is 45% of the median direct region-month, so any average taken across both channels describes a mixture nobody sells into (Figure 2)
3. Revenue rises about 174 USD per additional order and the straight-line fit accounts for 97.4% of the variation, so a region-month that missed its revenue missed its order count (Figure 3)
4. 3 regions grew across the pricing change while the West fell 8.6%, and the break lands in month 13 in that region only (Figure 4)
5. East month 18 is 3.3 times the region's median month while the months either side sit at 1.05 times it, so this is one observation and not a level change (Figure 5)

- share of rows with missing revenue: 4.2% (95% interval 1.6% to 7.3%)
- median partner region-month revenue: 16468 USD (95% interval 15826 USD to 17001 USD)
- mean revenue per order: 180.1 USD (95% interval 178.4 USD to 181.8 USD)
- West change across the pricing change (six months either side): -8.6% (95% interval -11.6% to -5.1%)
- East month 18 as a multiple of the region median: 3.3x (no interval: a single observation has no sampling interval; one point is one point)

## What we looked at and found nothing in

- A cumulative revenue curve was drawn and discarded: a cumulative series rises whatever the underlying months do, so it answered no question the monthly series had not already answered
- The order-count distribution was checked for a second population; it shows the same channel split the revenue column already shows, so it adds no evidence of its own
- Region-by-channel interaction was checked; the partner channel runs at the same share of direct in all four regions, so there is no interaction to report
- Revenue per order was compared across the four regions; they are indistinguishable on this measure, which is worth one line here so the next reader does not spend an afternoon on it
- Calendar seasonality was checked by lining the two years up month against month; nothing stood out above the month-to-month noise
- The missing revenue rows were checked for a time pattern as well as a channel pattern; they are scattered across the two years rather than clustered in any single month
- A region-by-month heatmap was drawn and discarded: it held the same information as the trend lines while making the month-13 break harder to see, which is the wrong trade for a report

## Evidence

### Figure 1 — Which rows have no revenue, and is the missingness concentrated anywhere?

![Which rows have no revenue, and is the missingness concentrated anywhere?](figures/01-missing-revenue.png)

**Figure 1.** 8 of 192 rows (4.2%) have no revenue, and 100% of those gaps are partner rows -- the missingness is a channel problem, not random loss

Every other column is complete. Because the gaps sit entirely in one channel, any figure that pools the two channels and drops missing rows silently under-counts partner activity, so the rest of this report uses direct-channel rows wherever a level is being compared.

*share of rows with missing revenue: 4.2% (95% interval 1.6% to 7.3%)*

### Figure 2 — Is monthly revenue one population, or several stacked on top of each other?

![Is monthly revenue one population, or several stacked on top of each other?](figures/02-channel-populations.png)

**Figure 2.** Revenue is two populations rather than one: the median partner region-month is 45% of the median direct region-month, so any average taken across both channels describes a mixture nobody sells into

The two histograms barely overlap. A single mean over this column would land in the empty gap between them and describe no real region-month at all -- Day 116's warning about a summary that discards the thing you needed, met again in a column you would have been tempted to average.

*median partner region-month revenue: 16468 USD (95% interval 15826 USD to 17001 USD)*

### Figure 3 — How tightly do orders and revenue move together, and what is one extra order worth?

![How tightly do orders and revenue move together, and what is one extra order worth?](figures/03-orders-vs-revenue.png)

**Figure 3.** Revenue rises about 174 USD per additional order and the straight-line fit accounts for 97.4% of the variation, so a region-month that missed its revenue missed its order count

There is no second cluster off the line and no curvature worth naming. That is a boring finding, and it is in the report precisely because it closes a question the reader would otherwise have to ask: revenue here is not being moved by price. The fitted slope (174 USD) sits a little below the mean revenue per order (180 USD) because the fit carries a non-zero intercept of 778 USD; the two numbers answer slightly different questions and the report says which is which rather than quoting whichever is larger.

*mean revenue per order: 180.1 USD (95% interval 178.4 USD to 181.8 USD)*

### Figure 4 — Did any region's trajectory change at the month-13 pricing change?

![Did any region's trajectory change at the month-13 pricing change?](figures/04-region-trend.png)

**Figure 4.** 3 regions grew across the pricing change while the West fell 8.6%, and the break lands in month 13 in that region only

Comparing the six months before month 13 with the six months after, the four regions move North +12.5%, South +1.7%, East +47.5%, West -8.6%. The West is the only one that changes direction, and it changes it at the month the price moved. This is an association in observational data, not a controlled comparison: nothing here rules out a third cause that happened to the West in the same month. East's +47.5% is not what it looks like either: drop the single month-18 observation and it falls to +8.0%, which is why Figure 5 exists.

*West change across the pricing change (six months either side): -8.6% (95% interval -11.6% to -5.1%)*

### Figure 5 — Is the East's month-18 jump a level change or a single outlier?

![Is the East's month-18 jump a level change or a single outlier?](figures/05-east-anomaly.png)

**Figure 5.** East month 18 is 3.3 times the region's median month while the months either side sit at 1.05 times it, so this is one observation and not a level change

The distinction matters for what you do next. A level change is a fact about the business and belongs in the forecast; a single spike is a fact about one month and belongs with whoever can explain it. Until someone does, the honest move is to report both the figure including it and the figure excluding it, and to say which one the decision was made on.

*East month 18 as a multiple of the region median: 3.3x (no interval: a single observation has no sampling interval; one point is one point)*

## Caveats

- This is observational data, not an experiment. The month-13 break is an association in time; it is not proof that the pricing change caused it.
- The regional comparison uses six months either side of the change. Six observations per side is a small window, and the interval on that number is correspondingly wide -- read the interval, not the point estimate.
- Level comparisons use direct-channel rows only, because the partner channel is the one with missing revenue. Partner totals in this report are therefore lower bounds.
- Every figure here uses a colourblind-safe palette and labelled axes, and no axis in this report is truncated below zero.

## Provenance

- Source: synthetic monthly sales, 4 regions x 2 channels x 24 months, generated by data.monthly_sales() with numpy default_rng(133)
- Shape: 192 rows, 5 columns
- Data fingerprint (sha256, first 12): `2ba806a5cbf5`
- This document was generated by code from the input above. Nothing in it was typed by hand, so re-running it on new data cannot leave the prose disagreeing with the figures.
