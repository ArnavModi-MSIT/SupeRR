# SupeRR Selector S2 · Round 1 · Pressure model

Who delivers when the game is on the line? A leverage-based pressure model for IPL and T20I
batters and bowlers (2022–2026), built for Rajasthan Royals' SupeRR Selector Season 2.

- **Report:** [`SupeRR_R1_Methodology_Report.pdf`](SupeRR_R1_Methodology_Report.pdf) (6 pages)
- **Dashboard:** [`docs/`](docs/) is a static page (`index.html` + `data.js` + `report.pdf`); no build step.

## Result

Ranked by pressure rating: win probability added per 100 pressure balls, in wins (1.0 = one win per 100 pressure balls), relative to an average player in the same situation, shrunk toward the level the player's all-ball record predicts. Players need at least 15 matches with pressure balls.

| # | Batters | Rating | | # | Bowlers | Rating |
|---|---|---|---|---|---|---|
| 1 | Tim David | 1.35 | | 1 | Josh Hazlewood | 0.78 |
| 2 | Ashutosh Sharma | 1.31 | | 2 | Varun Chakravarthy | 0.65 |
| 3 | Rinku Singh | 1.21 | | 3 | Rashid Khan | 0.58 |
| 4 | Rashid Khan | 1.17 | | 4 | Sunil Narine | 0.55 |
| 5 | Heinrich Klaasen | 0.77 | | 5 | Mohsin Khan | 0.54 |
| 6 | Dasun Shanaka | 0.75 | | 6 | Kuldeep Yadav | 0.50 |
| 7 | Suryakumar Yadav | 0.68 | | 7 | Wanindu Hasaranga | 0.48 |
| 8 | Shreyas Iyer | 0.63 | | 8 | Lockie Ferguson | 0.45 |
| 9 | Namboori Tilak Varma | 0.63 | | 9 | Mujeeb Ur Rahman | 0.41 |
| 10 | Rahul Tewatia | 0.60 | | 10 | Krunal Pandya | 0.40 |

Places 6–10 are close calls, and pressure-specific skill is a small part of each rating. Usual levels use legal balls only. Built on the updated ball-by-ball file issued on 16 Nov (actual extra runs recorded); the original file kept 7 of these batters and 8 of these bowlers. See §7 of the report for reliability and limitations.

## Method in brief

1. Fit a per-innings logistic win-probability model on ball-by-ball state (runs, wickets, balls left, target).
2. Leverage = expected |change in win probability| over the possible outcomes of a ball.
   A **pressure ball** is a legal ball in the top 20% of leverage among all first-innings balls or all chase balls (pooled across matches); an **ordinary ball** is in the bottom 50%.
3. Value per ball = win probability after the actual outcome minus the expected value after an average ball in that state.
4. Hierarchical empirical-Bayes rating (shrinkage constants chosen by cross-validation), opposition adjustment,
   eligibility (≥100 pressure balls for batters, ≥90 for bowlers, ≥15 matches with pressure balls, active in 2026).
5. 300-match bootstrap for rank ranges; sensitivity runs (absolute leverage, T20I-only, IPL-only, 2024+, no opposition adjustment, iterative adjustment, pace/spin context, venue scoring, usual level from non-pressure balls, chases only, excluding Associate/A-team matches, true IPL-only, per-match pressure cut-off, bowler baseline with wides and no-balls).

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
python consistency.py     # share of pressure matches with a positive value (report section 7)
python lb_check.py bat 300   # conservative lower-bound ranking check (also: bowl)
python oos_check.py       # win-probability model refit on pre-2025 matches, scored on 2025-26
python export_site.py     # docs/data.js
python build_report.py    # report PDF
```

Seeds are fixed (42 for bootstraps). To view the dashboard locally: `cd docs && python -m http.server 8000`.

## Layout

```
work/   pipeline scripts (core.py holds shared loaders and rating code), fig/, stats.json, top_*.csv
docs/   static dashboard (served by GitHub Pages)
SupeRR_R1_Methodology_Report.pdf
```

Rankings come from the data pack alone. Public articles are used only for the Rajasthan Royals context remarks in §6 of the report.
