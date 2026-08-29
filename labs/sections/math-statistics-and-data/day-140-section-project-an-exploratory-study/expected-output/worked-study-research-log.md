# Research log

Every look taken, in the order it was taken, including the ones that
found nothing. The number of `exploration` rows below is the
comparison count reported in REPORT.md.

| seq | timestamp | split | activity | outcome |
| --- | --- | --- | --- | --- |
| 1 | 2026-06-30T09:05:00Z | exploration | distribution of pm25_ug_m3 across all stations | right-skewed, no second mode; nothing to explain |
| 2 | 2026-06-30T09:18:00Z | exploration | pm25_ug_m3 split by station_type | roadside sits visibly higher; worth a hypothesis |
| 3 | 2026-06-30T09:31:00Z | exploration | pm25_ug_m3 against humidity_pct | no visible relationship; nothing found |
| 4 | 2026-06-30T09:44:00Z | exploration | pm25_ug_m3 by individual station_id | spread within each type, no single station driving the gap |
| 5 | 2026-06-30T09:52:00Z | none | hypothesis declared | Roadside stations have a higher mean PM2.5 than park stations. |
| 6 | 2026-06-30T10:07:00Z | confirmation | test the declared hypothesis once | see REPORT.md |
