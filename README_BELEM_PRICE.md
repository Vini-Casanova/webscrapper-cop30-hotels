# Belém/PA — October–November Price Analysis

## What this does
- Filters the calendar dataset to Oct–Nov (or a custom start/end).
- Computes mean/median and 25th/75th percentile prices overall, by listing, by day.
- Optionally splits by `room_type` and neighbourhood (if `listings.csv` is present).
- Exports CSVs and two PNG charts.

## How to use
1) Put your files in `./data/`:
   - `calendar.csv` (or `calendar.csv.gz`) with `listing_id,date,price,available`
   - Optional: `listings.csv` (or `.gz`) with `id,room_type,neighbourhood_cleansed`

2) Run:
```
python belem_price_analysis.py --data-dir ./data --start 2025-10-01 --end 2025-11-30
```
Omit `--start/--end` to default to the current year's Oct–Nov.

3) See results in `./output/`:
- `prices_summary.csv`, `daily_avg_price.csv`, `listing_avg_price_oct_nov.csv`
- `charts/daily_avg_price.png`, `charts/price_box_oct_nov.png`

## Notes
- Use `--only_booked` if your `available` flag indicates bookability and you want price stats only for booked nights.
- The parser normalizes `R$`, `$`, comma/dot separators.
