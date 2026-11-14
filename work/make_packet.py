import pandas as pd, numpy as np, json, re
P='../notes/REVIEW_PACKET.md'; s=open(P,encoding='utf-8').read()
bat=pd.read_pickle('final_bat.pkl').sort_values('rank'); bowl=pd.read_pickle('final_bowl.pkl').sort_values('rank')
VC=json.load(open('variant_checks.json')); BS=json.load(open('bye_sens.json')); CO=json.load(open('consistency.json'))
def tab(f,rng):
    L=['| # | Player | Press. balls | Matches | Raw | Expected | Rating | '+rng+' | P(top 10) |','|---|---|---|---|---|---|---|---|---|']
    for i,(p,r) in enumerate(f.head(10).iterrows(),1):
        L.append(f"| {i} | {r['name']} | {int(r.n)} | {int(r.matches)} | {r.v100_raw:.2f} | {r.base100:.2f} | {r.v100:.2f} | {int(round(r.rank_lo))}-{int(round(r.rank_hi))} | {r.p_top10*100:.0f}% |")
    return '\n'.join(L)
def nxt(f): 
    g=f.iloc[10:15]; return ', '.join(f"{r['name']} {r.v100:.2f}" for _,r in g.iterrows())
def cnt(f,c): t=f.head(10); return int((t[c]<=10).sum()), int(t[c].isna().sum())
def row(lab,c):
    b,bn=cnt(bat,c); w,wn=cnt(bowl,c)
    return f"| {lab} | {b}"+(f" ({bn} too few balls)" if bn else '')+f" | {w}"+(f" ({wn} too few balls)" if wn else '')+" |"
rows=[row('Iterative player-level opposition','rk_iter'),row('Baseline by home-ground scoring level','rk_ven'),row('Baseline by bowler type and batter hand','rk_ctx'),row('No opposition correction','rk_noadj'),row('Down-weight Associate/A-team balls 0.5','rk_w05'),row('Absolute threshold LI >= 1.3','rk_abs'),row('Top 10% leverage (smaller samples)','rk_top10'),row('IPL / T20-format only','rk_ipl'),row('T20I only','rk_t20i'),row('Since 1 Jan 2024','rk_2024p'),row('Usual level from non-pressure balls only','rk_np'),row('Pressure balls from chases only','rk_chase'),row('Excluding Associate-nation and A-team matches','rk_noassoc'),row('True IPL matches only','rk_iplonly'),
 f"| Bye / leg-bye values 1.0/1.0 or 3.0/2.0 (main 2.0/1.4) | {BS['lo']['bat']['kept']} and {BS['hi']['bat']['kept']} | {BS['lo']['bowl']['kept']} and {BS['hi']['bowl']['kept']} |",
 f"| Pressure cut set within each match-innings (20% of every match) instead of pooled by innings | {VC['cut_match']['bat']['kept']} | {VC['cut_match']['bowl']['kept']} |",
 f"| Bowler usual level from all deliveries incl. wides/no-balls (earlier spec) | {VC['bowl_all']['bat']['kept']} | {VC['bowl_all']['bowl']['kept']} |"]
sec71=f"""### 7.1 Final top 10 (rating = wins added per 100 pressure balls; 1.0 = one win per 100 pressure balls)

Batters:

{tab(bat,'Rank range (10-90%)')}

Bowlers (usual level and pressure/ordinary samples all on legal balls; changed 14 Nov, see 9.15):

{tab(bowl,'Rank range')}

Rashid Khan is in both lists; the two lists are ranked independently and ratings are not comparable across them. P(top 10) sums to {bat.head(10).p_top10.sum()*100:.0f}% (batters) and {bowl.head(10).p_top10.sum()*100:.0f}% (bowlers) over the ten shown; across all eligible players it is at most 1000%. Mohsin Khan (0.763) and Josh Hazlewood (0.762) are effectively tied.

Next in line (ranks 11-15): batters {nxt(bat)}; bowlers {nxt(bowl)}. The gaps between ranks 7-15 are tiny relative to uncertainty.

"""
sec72="### 7.2 Sensitivity (how many of our ten stay in the top ten)\n\n| Variant | Batters | Bowlers |\n|---|---|---|\n"+'\n'.join(rows)+f"""

Win-probability model out of sample (`oos_check.py`): refit on pre-2025 matches only and scored on the 329 matches of 2025-26, accuracy is 63% / 81% (first / second innings) against 64% / 82% in-sample; ratings built from 2025-26 matches correlate 0.93 (batters) and 0.96 (bowlers) with the in-sample ones and keep 8 and 9 of the top ten.
Shrinkage check (`cv.py`, 60 random halvings): at c = 0 (usual level only) the prediction correlation with held-out pressure value is 0.129 (batters) and 0.117 (bowlers), against 0.138 and 0.117 at the chosen c (0.35, 0.10). With the earlier all-ball bowler baseline the bowler figures were 0.138 at c = 0 and 0.136 at c = 0.10, i.e. the legal-ball-only baseline is slightly less predictive.

Reading: the ordering of the head of each list is stable to modelling choices; the batter list is much less stable to the sample (competition and period) than the bowler list. Rinku Singh is first on all T20-format data but 22nd on T20I-only and 44th since 2024. Mohsin Khan (23 matches) is in the top six in every cut except T20I-only (too few balls) and since 2024 (32nd).

"""
sec73="""### 7.3 Lower-bound ranking (rating - 0.842 x SE)
Batters: 7 of our 10 stay in the top ten (Kamindu Mendis 5th to 12th, Rashid Khan 7th to 14th, Harry Brook 10th to 18th drop out; Abhishek Sharma, Tilak Varma, Shashank Singh come in). Order of that lower-bound top 10: Rinku Singh, Sooryavanshi, Ashutosh Sharma, Tim David, Suryakumar Yadav, Klaasen, Shanaka, Abhishek Sharma, Tilak Varma, Shashank Singh.
Bowlers: 9 of 10 stay (Matheesha Pathirana drops to 11th; Mujeeb Ur Rahman comes in at 10th). Order: Rashid Khan, Hazlewood, Chakravarthy, Narine, Mohsin Khan, Hasaranga, Kuldeep Yadav, Bumrah, Ferguson, Mujeeb Ur Rahman.
Not in the report; used only if asked.

"""
sec74=f"""### 7.4 Match-to-match consistency (in the report, section 7)
Share of a player's pressure matches with positive summed value (unshrunk; the dashboard now shows the same figure for every eligible player). Top-10 batters: median {CO['bat']['top_median']*100:.0f}% ({CO['bat']['top_min']*100:.0f}% Ashutosh Sharma to 100% Sooryavanshi, 16 matches), against {CO['bat']['elig_median']*100:.0f}% for all 99 eligible batters. Top-10 bowlers: median {CO['bowl']['top_median']*100:.0f}% ({CO['bowl']['top_min']*100:.0f}% Chakravarthy to {CO['bowl']['top_max']*100:.0f}% Mohsin Khan), against {CO['bowl']['elig_median']*100:.0f}% for all 89 eligible bowlers. Ashutosh Sharma's rating rests on a minority of very good matches.

"""
def swap(a,b,new):
    global s
    i=s.index(a); j=s.index(b); s=s[:i]+new+s[j:]
swap('### 7.1 Final top 10','### 7.2 Sensitivity',sec71)
swap('### 7.2 Sensitivity','### 7.3 Lower-bound',sec72)
swap('### 7.3 Lower-bound','### 7.4 Match-to-match',sec73)
swap('### 7.4 Match-to-match','### 7.5 Man-of-the-Match',sec74)
def rep(a,b):
    global s
    assert s.count(a)==1,a[:70]; s=s.replace(a,b)
rep("averaged 0.16 (batters) and 0.26 (bowlers); Spearman-Brown corrected about 0.28 and 0.41.","averaged 0.16 (batters) and 0.21 (bowlers); Spearman-Brown corrected about 0.28 and 0.34.")
rep("Split-half reliability is modest (0.16 batters, 0.26 bowlers).","Split-half reliability is modest (0.16 batters, 0.21 bowlers).")
rep("- Pressure delivery: legal ball with LI in the top 20% of its own innings. Cut points: LI >= 1.002 (innings 1), >= 1.592 (innings 2).","- Pressure delivery: legal ball with LI in the top 20% of all legal balls of its innings number, pooled across matches (not within each match). Cut points: LI >= 1.002 (innings 1), >= 1.592 (innings 2). A per-match-innings cut is a sensitivity variant (7.2).")
rep("| Pressure rule | LI in top 20% of own innings (1.002 / 1.592) |","| Pressure rule | LI in top 20% of all balls of the same innings number, pooled (1.002 / 1.592) |")
rep("- Usual level `av` = mean V over all of the player's eligible deliveries (note: includes the pressure balls themselves;","- Usual level `av` = mean V over all of the player's eligible legal deliveries (bowlers: legal balls only since 14 Nov, so the sample matches the pressure and ordinary balls; earlier drafts included wides and no-balls). Note: includes the pressure balls themselves;")
rep("First-innings pressure is weaker: the first-innings model has 64% accuracy, and the top-20% cut there is only LI >= 1.00 (an average ball), so first-innings \"pressure\" is relative to its own innings, mostly powerplay and death overs.","First-innings pressure is weaker: the first-innings model has 64% accuracy, and the top-20% cut there is only LI >= 1.00 (an average ball), so first-innings \"pressure\" is relative to first innings only, mostly powerplay and death overs (63% / 34%).")
rep("and falls to 16th when Associate and A-team matches are excluded; the 15-match rule now removes him. Mohsin Khan (23 matches) is the new #1 and is top-5 in all but two cuts.","and falls to 15th when Associate and A-team matches are excluded; the 15-match rule now removes him. Mohsin Khan (23 matches) is #1 (tied with Hazlewood) and is top-6 in all but two cuts.")
rep("Changing them to 1.0/1.0 or 3.0/2.0 keeps 8-9 of ten in each list.","Changing them to 1.0/1.0 or 3.0/2.0 keeps 8-10 of ten in each list.")
rep("Sooryavanshi and Shanaka played for RR in 2026. These remarks","Sooryavanshi and Shanaka appear for RR in the 2026 data. These remarks")
open(P,'w',encoding='utf-8').write(s)
print('ok')
