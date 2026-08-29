# Damage report

What the cleaning *changed*, measured. A step with no before/after
number is a changelog entry, not a damage report.

Rows in: 264. Rows out: 245. Rows removed: 19 (7.20% of the delivery).

### normalise station_type casing

measure: distinct station_type values
before: 8
after: 2
changed: 6

strip and lower-case; no row is dropped by this step

### drop duplicate reading_id rows

measure: rows
before: 264
after: 256
changed: 8

the duplicates are byte-identical redeliveries; first wins

### drop sensor fault sentinel readings

measure: rows carrying the -1.0 fault sentinel
before: 6
after: 0
changed: 6

-1.0 is not a low reading; it is the unit reporting a fault

### drop rows with no pm25 reading

measure: rows with a blank pm25_ug_m3
before: 5
after: 0
changed: 5

blank means the reading never arrived; it is not a zero
