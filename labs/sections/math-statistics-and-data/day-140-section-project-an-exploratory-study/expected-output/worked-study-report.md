# Roadside and park PM2.5: an exploratory study

As of 2026-06-30. Exploratory. Not causal.

## Question

Do roadside air-quality stations record higher PM2.5 than park stations, and
by how much?

The question was written to QUESTION.md before the source file was opened,
so that the analysis could not quietly become a search for whichever
question the data happened to answer well.

## What the data is

A synthetic network of eight fixed air-quality stations, four sited at
roadside and four in parks, reporting daily PM2.5 through June 2026.
Provenance, licence, dictionary and checksum are recorded in SOURCE.json;
the grain -- one row per reading -- is asserted in INGEST.json, and the
record says plainly that the assertion failed on arrival and what resolved
it.

## What cleaning changed

The delivery carried 264 rows. 245 survived cleaning. The four steps and
their before/after measurements are in CLEANING.md. The largest single loss
is the eight duplicated readings, which is a grain violation rather than a
data-quality problem, and would have biased every mean below had it gone
unnoticed.

## How it was explored

The cleaned frame was split into an exploration half (122 readings) and a
confirmation half (123 readings) before any look was taken. RESEARCH_LOG.md
records every look in order. The exploration half was examined 4 times. The
confirmation half was opened once, after the hypothesis was written down,
and tested once.

## Findings

On the confirmation half, roadside stations recorded a mean PM2.5 5.50 ug/m3
higher than park stations (95% CI 3.80 to 7.21, n=60 roadside and n=63 park
readings).

The interval excludes zero, so the direction of the difference is the same
across the whole interval. The estimate is imprecise enough that a true
difference anywhere between 3.80 and 7.21 ug/m3 would be consistent with
what was seen, which is a much weaker statement than the point value alone
would suggest.

Comparisons examined before this hypothesis was declared: 4. That number
belongs next to the interval, not in a footnote: it is what tells a reader
how much searching preceded the one test.

## Figures

Each figure in FIGURES.json carries the question it was drawn to answer and
the claim it supports. Both are drawn from the exploration half only, so no
figure shows the data the estimate above was measured on.

![PM2.5 by station type](figures/fig-01-pm25-by-station-type.png)

![PM2.5 distribution](figures/fig-02-pm25-distribution.png)

## Limits

This study is exploratory. It does not establish that roadside siting
*causes* higher PM2.5. Station siting is not randomised: the roadside units
are where they are for reasons -- traffic volume, building density, land
availability -- that are themselves plausible causes of the difference
measured here.

The measured quantity is a proxy. PM2.5 at a fixed station is not what
anyone breathes; exposure depends on where people actually are and for how
long, which this data does not contain.

Who is missing: eight stations is a sample of sites, not of people.
Neighbourhoods without a station contribute nothing, and stations are not
sited at random, so the absence is not random either.

What would establish causation: an intervention -- a road closure, a
traffic-calming scheme, a low-emission zone boundary -- with readings from
the same stations before and after, and control stations outside the
intervention area over the same period. This study names that design; it
does not run it.

## Reproducing this

MANIFEST.json records a SHA-256 for every file this study generated.
Rebuilding the study from the same source file and the same seeds reproduces
every one of them, figures included. Nothing here reads the clock: the as-of
date is a parameter.
