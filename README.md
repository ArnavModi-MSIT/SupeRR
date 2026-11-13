# SupeRR Selector S2 · Round 1 · Pressure model

Who delivers when the game is on the line? A leverage-based pressure model for IPL and T20I
batters and bowlers (2022–2026), built for Rajasthan Royals' SupeRR Selector Season 2.

- **Report:** [`SupeRR_R1_Methodology_Report.pdf`](SupeRR_R1_Methodology_Report.pdf) (6 pages)
- **Dashboard:** [`site/`](site/) is a static page (`index.html` + `data.js` + `report.pdf`); no build step.

## Result

Ranked by pressure rating: win probability added (percentage points) per 100 pressure balls, relative to an average player in the same situation, shrunk toward the player's all-ball level.

| # | Batters | Rating | | # | Bowlers | Rating |
|---|---|---|---|---|---|---|
| 1 | Rinku Singh | 1.50 | | 1 | Sufiyan Muqeem | 0.85 |
| 2 | Ashutosh Sharma | 1.23 | | 2 | Mohsin Khan | 0.74 |
| 3 | Vaibhav Sooryavanshi | 1.06 | | 3 | Josh Hazlewood | 0.72 |
| 4 | Tim David | 0.92 | | 4 | Varun Chakravarthy | 0.65 |
| 5 | Kamindu Mendis | 0.90 | | 5 | Rashid Khan | 0.64 |
| 6 | Dasun Shanaka | 0.75 | | 6 | Sunil Narine | 0.63 |
| 7 | Rashid Khan | 0.70 | | 7 | Wanindu Hasaranga | 0.53 |
| 8 | Heinrich Klaasen | 0.66 | | 8 | Kuldeep Yadav | 0.44 |
| 9 | Suryakumar Yadav | 0.65 | | 9 | Lockie Ferguson | 0.43 |
| 10 | Harry Brook | 0.61 | | 10 | Jasprit Bumrah | 0.41 |

Places 7–10 are close calls, and pressure-specific skill is a small part of each rating. See §7 of the report for reliability and limitations.

## Method in brief

1. Fit a per-innings logistic win-probability model on ball-by-ball state (runs, wickets, balls left, target).
2. Leverage = expected |change in win probability| over the possible outcomes of a ball.
   A **pressure ball** is a legal ball in the top 20% of leverage within its innings; an **ordinary ball** is in the bottom 50%.
3. Value per ball = win probability after the actual outcome minus the expected value after an average ball in that state.
4. Hierarchical empirical-Bayes rating (shrinkage constants chosen by cross-validation), opposition adjustment,
   eligibility (≥100 pressure balls for batters, ≥90 for bowlers, active in 2026).
5. 300-match bootstrap for rank ranges; sensitivity runs (absolute leverage, T20I-only, IPL-only, 2024+, no opposition adjustment, iterative adjustment, pace/spin context, venue scoring).

## Reproduce

Needs Python 3.10+ and `pip install -r requirements.txt`. Put the organiser's data pack
(`6af3166e7b922_data_pack/`) next to `work/`; it is not included in this repo. Then, from `work/`:

```bash
python prep.py ../6af3166e7b922_data_pack balls.pkl   # clean and join
python wp.py .            # win-probability model
python wp_ctx.py .        # variant: pace/spin x hand context
python wp_ven.py .        # variant: venue scoring tercile
python rel.py             # split-half reliability
python cv.py              # cross-validated shrinkage
python boot.py            # ratings, bootstrap, sensitivity (writes final_*.pkl)
python stats.py           # figures and stats.json
python export_site.py     # site/data.js
python build_report.py    # report PDF
```

Seeds are fixed (42 for bootstraps). To view the dashboard locally: `cd site && python -m http.server 8000`.

## Layout

```
work/   pipeline scripts (core.py holds shared loaders and rating code), fig/, stats.json, top_*.csv
site/   static dashboard
SupeRR_R1_Methodology_Report.pdf
```

Rankings come from the data pack alone. Public articles are used only for the Rajasthan Royals context remarks in §6 of the report.
