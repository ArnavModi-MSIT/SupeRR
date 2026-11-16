import json, pandas as pd, numpy as np, os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib, os
FD=os.path.join(matplotlib.get_data_path(),'fonts','ttf')+os.sep
pdfmetrics.registerFont(TTFont('DV',FD+'DejaVuSans.ttf')); pdfmetrics.registerFont(TTFont('DVB',FD+'DejaVuSans-Bold.ttf')); pdfmetrics.registerFont(TTFont('DVI',FD+'DejaVuSans-Oblique.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('DV',normal='DV',bold='DVB',italic='DVI',boldItalic='DVB')
PINK=colors.HexColor('#E6007E'); NAVY=colors.HexColor('#0B1F4B'); LG=colors.HexColor('#F1F3F8')
S=json.load(open('stats.json',encoding='utf-8'))
H1=ParagraphStyle('h1',fontName='DVB',fontSize=13,textColor=NAVY,spaceBefore=8,spaceAfter=3,keepWithNext=1)
H2=ParagraphStyle('h2',fontName='DVB',fontSize=10,textColor=PINK,spaceBefore=6,spaceAfter=2,keepWithNext=1)
B=ParagraphStyle('b',fontName='DV',fontSize=8.5,leading=11.2,spaceAfter=3.5)
BL=ParagraphStyle('bl',parent=B,leftIndent=10,bulletIndent=0,spaceAfter=2)
SM=ParagraphStyle('sm',fontName='DV',fontSize=7,leading=9)
SMB=ParagraphStyle('smb',parent=SM,fontName='DVB')
SMW=ParagraphStyle('smw',parent=SM,fontName='DVB',textColor=colors.white)
CAP=ParagraphStyle('cap',fontName='DVI',fontSize=7.2,leading=9,textColor=colors.HexColor('#555555'),spaceAfter=6)
T=ParagraphStyle('t',fontName='DVB',fontSize=19,textColor=NAVY,leading=23)
def P(t,s=B): return Paragraph(t,s)
def bl(t): return Paragraph(t,BL,bulletText='•')
bat=pd.read_pickle('final_bat.pkl').sort_values('rating',ascending=False).head(10)
bowl=pd.read_pickle('final_bowl.pkl').sort_values('rating',ascending=False).head(10)
def tbl(data,cw,hdr=1,zebra=True,fs=7.2):
    t=Table(data,colWidths=cw,repeatRows=hdr)
    st=[('FONT',(0,0),(-1,-1),'DV',fs),('FONT',(0,0),(-1,hdr-1),'DVB',fs),('BACKGROUND',(0,0),(-1,hdr-1),NAVY),('TEXTCOLOR',(0,0),(-1,hdr-1),colors.white),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#C9CED9')),('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)]
    if zebra:
        for i in range(hdr,len(data)):
            if (i-hdr)%2==1: st.append(('BACKGROUND',(0,i),(-1,i),LG))
    t.setStyle(TableStyle(st)); return t
def f(x,d=2):
    t=f'{x:.{d}f}'
    return t[1:] if False else (t.replace('-0.00','0.00') if t=='-0.00' else t)
doc=SimpleDocTemplate('SupeRR_R1_Methodology_Report.pdf',pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=13*mm,bottomMargin=12.5*mm,title='SupeRR Selector S2 - Round 1 Methodology Report',author='Arnav')
W=A4[0]-32*mm
el=[]
el+= [P('SupeRR Selector Season 2 — Round 1',ParagraphStyle('k',fontName='DVB',fontSize=8,textColor=PINK)),P('Who delivers when the game is on the line?',T),
 P('A leverage-based pressure model for IPL and T20I batters and bowlers, 2022–2026',ParagraphStyle('s',fontName='DV',fontSize=10,textColor=colors.HexColor('#444'),spaceAfter=8))]
el+= [P('1. Summary of approach and results',H1),
 P(f"We define <b>pressure</b> as a delivery whose outcome can swing the match's win probability by an unusually large amount (a <i>leverage index</i>, LI), measured by our own win-probability model fitted on the {S['matches']} complete matches in the data pack. We measure each player's <b>performance under pressure</b> as the win probability they add on those deliveries compared with an average player in the identical situation. Because a pressure sample is small and noisy, each rating blends the player's <b>usual level</b> (all his legal deliveries, shrunk) with a <b>pressure-specific lift</b>; the blend weight was chosen by out-of-sample prediction, not by hand. Rankings use players active in 2026 with enough pressure deliveries, and are stress-tested with 300 match-level bootstraps and some fifteen alternative definitions, samples and data assumptions."),
 P("<b>Headline finding.</b> Pressure performance is mostly a continuation of general quality: after accounting for a player's usual level, only a modest, batter-specific pressure effect is detectable, and for bowlers it is close to nil. We therefore do not pretend to find hidden 'clutch' specialists; we rank players by their best-supported estimate of how well they will perform when the match is tight.")]
def rank_table(top,role):
    hdr=['#','Player','Press.\nballs','Matches','Raw value\n/100 balls','Expected\nlevel','Rating\n/100 balls','Rank range\n(80% boot.)','P(top 10)']
    rows=[hdr]
    for i,(p,r) in enumerate(top.iterrows(),1):
        rows.append([str(i),r['name'],f"{int(r.n)}",f"{int(r.matches)}",f(r.v100_raw),f(r.base100),f(r.v100),f"{int(round(r.rank_lo))}–{int(round(r.rank_hi))}",f"{r.p_top10*100:.0f}%"])
    return tbl(rows,[7*mm,38*mm,16*mm,16*mm,23*mm,17*mm,20*mm,26*mm,17*mm])
el+= [P('Final top-10 batters under pressure',H2),rank_table(bat,'bat'),Spacer(1,4),P('Final top-10 bowlers under pressure',H2),rank_table(bowl,'bowl'),
 P(f"Values are win probability added per 100 pressure deliveries, in wins (1.0 = one win per 100 deliveries), relative to an average player in the same situation. 'Raw value' is unshrunk; 'Expected level' is what the player's all-ball record predicts for pressure; 'Rating' is what we rank on. Rank range is the 10th–90th percentile of the player's rank over 300 bootstrap resamples of matches; P(top 10) is the share of resamples in which he finishes in the top ten (a resample where he falls below the minimum sample counts as a miss). The ten shown sum to {bat.p_top10.sum()*100:.0f}% (batters) and {bowl.p_top10.sum()*100:.0f}% (bowlers) of the 1000% available, so a player outside the lists can still hold substantial probability. Rashid Khan appears in both lists, which are ranked independently; ratings are not comparable between the two lists.",CAP)]
# ---- data
el+= [P('2. Data preparation',H1),
 bl(f"<b>Scope.</b> {S['rows']:,} deliveries from {S['matches']} matches ({S['t20i_m']} T20I and {S['ipl_m']} T20-format matches, i.e. IPL 2022–26 plus a few A-team series), joined to matches, competitions and teams. The data runs to 1 Nov 2026."),
 bl("<b>Excluded for validity.</b> Matches with no result, revised targets or reduced overs (so the required rate is not comparable), single-innings fixtures, and super-over innings: 49 matches in all, leaving 818."),
 bl("<b>Legal balls and extras.</b> Wides, no-balls (including the 'other' type, which are height/full-toss no-balls) do not consume a legal ball. Team scores add the recorded extra runs (wides, no-balls, byes, leg-byes and penalties) from the updated ball-by-ball file issued on 16 Nov. With it, reconstructed scores reproduce every 'won by N runs' margin exactly, and every chase winner but two reaches its target, so targets and required rates are exact."),
 bl("<b>Attribution.</b> A batter is responsible for runs off the bat and for his own dismissals (non-striker run-outs are not charged to him); wides, no-balls, byes and leg-byes are excluded from his balls faced. A bowler is charged for runs conceded including wides and no-balls but not byes/leg-byes, and credited with wickets other than run-outs and retirements.")]
# ---- pressure
pp,po=S['prof_p'],S['prof_o']
el+= [P('3. How we define pressure',H1),
 P("<b>Step 1 – win probability.</b> For every legal delivery we estimate the batting side's chance of winning from the match state. We first compute the expected runs still to come for a given number of balls left and wickets lost (from the data), then fit a logistic model on that state: in a chase, the gap between the runs required and the expected remaining runs, scaled by the uncertainty remaining; in the first innings, the projected total against the par score. Interactions with balls left and wickets, plus an IPL/T20I indicator, let the same gap matter more late in an innings. The model is well calibrated (mean absolute calibration error "+f"{S['cal_err2']*100:.1f} points in chases, {S['cal_err1']*100:.1f} in first innings; log-loss 0.40 and 0.63; 81% and 64% accuracy)."),
 P("<b>Step 2 – leverage.</b> For each delivery we list the possible outcomes (dot, 1, 2, 3, 4, 6, wicket), weight them by how often each occurs in comparable situations (same innings, phase, wickets down, win-probability band and league), and compute the expected absolute change in win probability. Dividing by the average over all deliveries gives the <b>leverage index</b>: 1.0 is a typical ball, 2.0 means the ball is twice as decisive. Leverage captures every factor the brief lists in one number: required rate, wickets in hand, balls remaining, stage of the innings and how close the contest is."),
 P(f"<b>Step 3 – the pressure threshold.</b> A delivery is a <b>pressure delivery</b> if its leverage is in the top 20% of all first-innings deliveries (LI ≥ {S['cut']['1']:.2f}) or of all chase deliveries (LI ≥ {S['cut']['2']:.2f}), pooled across matches. A separate cut-off for each innings means batting first and chasing are both represented: first-innings pressure sits mostly in the powerplay (63% of first-innings pressure balls) and the death overs (35%), where wickets and big overs swing the projected total, while chase pressure is a tight equation. This gives {S['press_balls']:,} pressure deliveries. An <b>ordinary delivery</b> is in the bottom half ({S['ord_balls']:,} deliveries); ordinary balls are used only for comparison (Table 1 and the economy figures in §6), while each player's baseline is his usual level over all legal balls (§4)."),
 Image('fig/fig1.png',width=W*0.85,height=W*0.85*3.1/8),P("Figure 1. Left: calibration of the win-probability model. Right: mean leverage by over; the last overs of chases are the most decisive.",CAP)]
prof=[['','Ordinary','Pressure'],
 ['Mean leverage index',f(po['li']),f(pp['li'])],['Share of balls with win probability 25–75%',f"{po['wpmid']:.0f}%",f"{pp['wpmid']:.0f}%"],
 ['Powerplay / middle / death share',f"{po['pp']:.0f}% / {po['mid']:.0f}% / {po['death']:.0f}%",f"{pp['pp']:.0f}% / {pp['mid']:.0f}% / {pp['death']:.0f}%"],
 ['Mean balls remaining',f"{po['bl']:.0f}",f"{pp['bl']:.0f}"],['Mean required rate in chases',f"{po['rrr']:.1f}",f"{pp['rrr']:.1f}"],
 ['Wicket probability per ball',f"{S['wk_o']:.1f}%",f"{S['wk_p']:.1f}%"]]
el+= [KeepTogether([tbl(prof,[75*mm,45*mm,45*mm]),P("Table 1. Pressure deliveries are overwhelmingly close-contest situations and over-weight the powerplay and death. They are also more wicket-prone, as expected.",CAP)])]
# ---- performance
el+= [P('4. Measuring performance and setting baselines',H1),
 P("<b>Value of a delivery.</b> For each delivery, <i>value</i> = win probability after what actually happened (from that player's responsibility, see §2) minus the <i>expected</i> win probability after an average delivery in the same situation. This is a win-probability-added measure, but relative to an average player in the same state, so a batter is not rewarded merely for arriving in a favourable state and a bowler is not punished for bowling the 19th over. It is positive for a batter who scores more or loses his wicket less often than average, and for a bowler who concedes less or takes more wickets. It values a wicket by its context (a top-order wicket at 40/3 is worth more than a tail-ender's at 160/8), and a dot ball by how decisive the moment is."),
 P("<b>Player baselines.</b> The brief asks how players perform under pressure <i>compared with their usual levels</i>. For each player we compute (a) <b>usual level</b>: mean value over all his legal deliveries, and (b) <b>pressure level</b>: mean value over his pressure deliveries. The gap between the two is the player's rise or dip under pressure; the rating below combines them."),
 P("<b>Rating.</b> Pressure samples are small (about 100–450 balls for most players, up to about 975 for some bowlers) and win-probability value per ball is very noisy, so raw pressure values are dominated by luck. We use an empirical-Bayes (hierarchical) estimate. The prior for a player's pressure level is a regression on his shrunk usual level; the pressure-specific deviation is then shrunk by a weight <i>c</i>. Rating = usual-level prior + <i>c</i> × (raw pressure level − prior); the 'expected level' column in §1 is this prior. We chose <i>c</i> by repeated random splits of the matches: predict one half's pressure value from the other half and see which <i>c</i> predicts best. The out-of-sample optimum was <i>c</i> ≈ 0.3–0.5 for batters (we use 0.35) and ≈ 0–0.1 for bowlers (we use 0.10). For batters a modest pressure-specific component improves out-of-sample prediction slightly (§7); for bowlers the data cannot distinguish pressure skill from general skill, so bowler ratings mainly reflect consistent underlying quality in leveraged situations. The usual level is measured on legal balls only for both roles, the same sample as the pressure and ordinary balls.")]
def cnt(top,c,k=10): return int((top[c]<=k).sum())
VC=json.load(open('variant_checks.json'))
_o={k:pd.read_pickle(f'v1_outputs/final_{k}.pkl').sort_values('rank').name[:10] for k in ('bat','bowl')}
V1={'bat':len(set(_o['bat'])&set(bat.name)),'bowl':len(set(_o['bowl'])&set(bowl.name))}
# ---- fairness
el+= [P('5. Fair comparisons',H1),
 bl("<b>Sample size.</b> Players need ≥ 100 pressure balls faced (batters) or ≥ 90 pressure balls bowled (bowlers), spread over at least 15 matches. Shrinkage (§4) further pulls small samples toward their expected value. The smallest samples in the final lists are Ashutosh Sharma (116 balls, 17 matches) and Krunal Pandya (133, 20). The rules were fixed before the results and not tuned: Vaibhav Sooryavanshi (93 pressure balls in the updated file) misses the batter minimum by seven balls although his all-ball record is the strongest of any batter, Harry Brook has 105 balls but only 14 matches, and the 15-match rule removes Sufiyan Muqeem (123 balls, 11 matches), who would otherwise rank second among bowlers."),
 bl("<b>Eligibility for the auction.</b> Only players who appeared in 2026 are ranked (players with no 2026 appearance, such as Dinesh Karthik, Tim Southee and Umesh Yadav, whose last matches in the data are in 2024, are excluded). We cannot see retention lists, so some listed players may already be contracted; this is for RR to verify."),
 bl(f"<b>IPL vs T20I.</b> We keep both: IPL is the best proxy for auction conditions, while T20I adds volume for overseas players and Associates. The win-probability model and the baselines are league-specific (IPL indicator), so a value is always measured against the same competition's average. Opposition strength is handled with a data-driven correction: each team's mean batting and bowling value is estimated (shrunk with n/(n+3000)), and a bowler's (batter's) value is adjusted by the strength of the batting (bowling) side faced. Corrections are small (up to about ±0.1 on this scale) but push in the expected direction: Zimbabwe, UAE, Oman, Netherlands and A-teams are weakest; India, Australia, England and RCB are strongest. Without this correction, {cnt(bat,'rk_noadj')}/10 batters and {cnt(bowl,'rk_noadj')}/10 bowlers stay in the top ten."),
 bl("<b>Different match contexts.</b> Using value relative to the situation's average controls for phase, wickets in hand and the target; first-innings and chase pressure are scored on the same scale. Rating is ranked within role, never across batting and bowling.")]
# ---- evidence
def blurb(role,p,r,i):
    d=S['desc'][f'{role}{int(p)}']
    if role=='bat':
        order=d['order']; role_s='powerplay opener' if order<=2.5 else ('top-order / anchor' if order<=4.2 else ('middle-order accelerator' if order<=5.5 else 'late-order finisher'))
        s=f"{d['hand']} {role_s} (average pressure position #{order:.1f}); {d['death']:.0f}% of pressure balls in overs 17–20, {d['pp']:.0f}% in the powerplay. Pressure SR {r.sr:.0f}, boundary rate {r.bpct:.0f}% and dismissal rate {r.dis_rate:.1f}% per ball."
        if d['n_spin']>=30 and d['sr_pace']-d['sr_spin']>35: s+=f" Weaker against spin under pressure (SR {d['sr_spin']:.0f} vs {d['sr_pace']:.0f} against pace), a point to plan around."
        elif d['n_spin']>=30 and d['sr_spin']>=d['sr_pace']-8: s+=f" Holds SR {d['sr_spin']:.0f} against spin and {d['sr_pace']:.0f} against pace under pressure, with no clear weakness to bowling type."
        else: s+=f" Pressure SR {d['sr_pace']:.0f} vs pace ({d['n_pace']} balls)."
    else:
        ph=f"{d['pp']:.0f}% powerplay / {d['mid']:.0f}% middle / {d['death']:.0f}% death"
        s=f"{d['btype']}; pressure usage {ph}. Under pressure: economy {r.econ:.2f} (vs {d['o_econ']:.2f} in ordinary overs), {int(r.wkts)} wickets, {r.dotpct:.0f}% dot balls."
    return s+' '+rrfit(role,r,d)
def rrfit(role,r,d):
    # data-derived squad-fit remark; names no squad facts beyond the public needs quoted in section 6
    if role=='bat':
        o=d['order']
        if d['death']>=45: t="a late-overs finisher"
        elif d['pp']>=40: t="a powerplay option at the top of the order"
        elif o<=4.2: t="an anchor for the middle overs"
        else: t="a middle-overs accelerator who can also finish"
    else:
        sp=d['pace']!='Pace'
        if d['death']>=35: t="a death-overs option"
        elif d['pp']>=35: t="a new-ball option in the powerplay"
        else: t="middle-overs control"
        t+=("; a spin option for high-leverage overs" if sp else "; a pace option for high-leverage overs")
    return f"<i>How he could help RR:</i> {t}."
fit_bat={4708:'finisher',8101:'finisher',50284:'opener',6396:'finisher',4904:'middle-order',2436:'finisher',4722:'lower-order hitter',4260:'wicketkeeper-batter, middle order',1699:'top-order stroke-maker',6280:'middle-order'}
el+= [P('6. Evidence for the top 10',H1),
 Image('fig/top_bat.png',width=W*0.58,height=W*0.58*3.9/7),P("Figure 2. Top-10 batters. The dark tick is the rating. Grey = expected level from the all-ball record; pink = pressure-specific lift that raises the rating above it; hatched = shortfall where the rating sits below the expected level; diamonds = raw (unshrunk) pressure value.",CAP),
 Image('fig/top_bowl.png',width=W*0.58,height=W*0.58*3.9/7),P("Figure 3. Top-10 bowlers (same construction).",CAP)]
el+= [P('Batters: what each pick adds',H2),P("Each note ends with how the player could help RR, taken from the data (role, phase mix) alone. It assumes nothing about RR's current squad; check retention status.",CAP)]
for i,(p,r) in enumerate(bat.iterrows(),1):
    el.append(P(f"<b>{i}. {r['name']}</b> — {blurb('bat',p,r,i)}",B))
el+= [P('Bowlers: what each pick adds',H2)]
for i,(p,r) in enumerate(bowl.iterrows(),1):
    el.append(P(f"<b>{i}. {r['name']}</b> — {blurb('bowl',p,r,i)}",B))
el+= [P("Economy under pressure is above ordinary-over economy for two of the ten bowlers (Rashid Khan and Hasaranga). Economy alone does not set the rating: each ball is compared with an average bowler in the same situation and wickets count by their context, so an economy near 8.7 in high-leverage overs can still add value (Hasaranga, 20 wickets).",CAP),P("Roles come from the ball-by-ball data. <b>RR context (public articles, not the data pack).</b> IPL 2027 previews say RR needs finishers, an overseas all-rounder and durable Indian seamers (CricTracker; Mykhel; opinion pieces, not RR statements). The batter list fits the finisher gap (Tim David, Ashutosh Sharma, Rinku Singh, Rahul Tewatia); the bowler list fits the need for proven death-overs options (Hazlewood, Ferguson, Mohsin Khan, Rashid Khan). Shanaka appears for Rajasthan Royals in the 2026 data, so RR may already hold him. <b>Retention check:</b> retentions are due 17 Nov; any listed player retained by a club is unavailable at auction, but the performance ranking is unchanged.",CAP)]
el+= [Table([[Image('fig/scatter_bat.png',width=W*0.32,height=W*0.32*3.6/4.6),Image('fig/scatter_bowl.png',width=W*0.32,height=W*0.32*3.6/4.6)]],colWidths=[W*0.5,W*0.5]),
 P("Figure 4. Usual vs pressure level for every qualifying player (grey) and the final top 10 (pink, numbered by final rank). Most players cluster near the diagonal: pressure performance tracks general quality.",CAP)]
# ---- reliability
rows=[['Alternative definition / sample','Batters still in top 10','Bowlers still in top 10'],
 ['Iterative opposition adjustment; ground scoring level (§8)',f"{cnt(bat,'rk_iter')}/10; {cnt(bat,'rk_ven')}/10",f"{cnt(bowl,'rk_iter')}/10; {cnt(bowl,'rk_ven')}/10"],
   ['Baseline by bowler type (pace/spin) and batter hand',f"{cnt(bat,'rk_ctx')}/10 ({int(bat.rk_ctx.isna().sum())} below min. balls)",f"{cnt(bowl,'rk_ctx')}/10"+(f" ({int(bowl.rk_ctx.isna().sum())} below min. balls)" if bowl.rk_ctx.isna().any() else '')],
 ['No opposition-strength correction',f"{cnt(bat,'rk_noadj')}/10",f"{cnt(bowl,'rk_noadj')}/10"],
 ['Absolute threshold LI ≥ 1.3 (95% chases)',f"{cnt(bat,'rk_abs')}/10",f"{cnt(bowl,'rk_abs')}/10"],
 ['Stricter pressure (top 10% leverage); smaller samples',f"{cnt(bat,'rk_top10')}/10 ({int(bat.rk_top10.isna().sum())} below min. balls)",f"{cnt(bowl,'rk_top10')}/10 ({int(bowl.rk_top10.isna().sum())} below min. balls)"],
 ['T20I matches only',f"{cnt(bat,'rk_t20i')}/10 ({int(bat.rk_t20i.isna().sum())} too few balls)",f"{cnt(bowl,'rk_t20i')}/10 ({int(bowl.rk_t20i.isna().sum())} too few balls)"],
 ['Since 1 Jan 2024 only',f"{cnt(bat,'rk_2024p')}/10",f"{cnt(bowl,'rk_2024p')}/10"],
 ['Usual level estimated from non-pressure balls only',f"{cnt(bat,'rk_np')}/10",f"{cnt(bowl,'rk_np')}/10"],
 ['Pressure balls from second-innings chases only',f"{cnt(bat,'rk_chase')}/10 ({int(bat.rk_chase.isna().sum())} too few balls)",f"{cnt(bowl,'rk_chase')}/10"],
 ['Excluding Associate-nation and A-team matches',f"{cnt(bat,'rk_noassoc')}/10",f"{cnt(bowl,'rk_noassoc')}/10"],
 ['IPL matches only (true IPL)',f"{cnt(bat,'rk_iplonly')}/10 ({int(bat.rk_iplonly.isna().sum())} too few balls)",f"{cnt(bowl,'rk_iplonly')}/10"],
 ['Pressure cut-off set within each match-innings (20% of every match) instead of pooled',f"{VC['cut_match']['bat']['kept']}/10",f"{VC['cut_match']['bowl']['kept']}/10"],
 ['Bowler usual level from all deliveries, including wides and no-balls (earlier specification)',f"{VC['bowl_all']['bat']['kept']}/10",f"{VC['bowl_all']['bowl']['kept']}/10"],
 ['Original data file (byes and leg-byes estimated, before the 16 Nov update)',f"{V1['bat']}/10",f"{V1['bowl']}/10"]]
rows=[[c.replace(' (0 below min. balls)','').replace(' (0 too few balls)','') for c in row] for row in rows]
el+= [P('7. Reliability and limitations',H1),
 P("<b>How consistent is the ranking?</b> We tested it four ways."),
 bl("<b>Split-half.</b> Over 30 random halvings of the matches, the rank correlation between ratings from the two halves averaged 0.19 for batters and 0.15 for bowlers (Spearman–Brown corrected to the full sample: about 0.32 and 0.26). Pressure samples are small, so this is modest and we state it plainly."),
 bl("<b>Out-of-sample prediction.</b> Ratings from one half of the matches correlate 0.17 (batters) and 0.06 (bowlers) with players' realised pressure value in the other half, against 0.15 and 0.02 for the unshrunk pressure values. Using the usual level alone (c = 0) gives 0.16 and 0.07, so the pressure-specific term adds a little for batters and nothing for bowlers, whose pressure value is hard to predict at all."),
 bl("<b>Bootstrap.</b> 300 resamples of matches give each player a rank range and a probability of finishing in the top 10 (tables in §1). Tim David, Ashutosh Sharma, Rinku Singh, Rashid Khan and Klaasen lead the batters (P(top 10) 63–91%); Hazlewood, Varun Chakravarthy, Rashid Khan, Narine and Mohsin Khan lead the bowlers (45–77%). Places 6–10 are close calls (36–58% for batters, 43–52% for bowlers). A wide rank range (Rahul Tewatia, 3–71) reflects a heavy tail of bad resamples, not a typically low rank."),
 bl("<b>Match-to-match consistency.</b> Share of a player's pressure matches with pressure value above an average player's in the same situation: For our top-ten batters the median is 53% (39% for Rahul Tewatia to 71% for Klaasen), against 55% for all 98 eligible batters; for our top-ten bowlers it is 59% (46% for Lockie Ferguson to 75% for Mujeeb Ur Rahman), against 44% for all 88 eligible bowlers. Top batters' ratings come from big contributions in some matches, not steady ones."),
 KeepTogether([P("<b>Sensitivity.</b> Number of our ten who stay in the top ten when a modelling choice changes:",B),
 tbl([[Paragraph(str(c),SMW if i==0 else SM) for c in r] for i,r in enumerate(rows)],[88*mm,45*mm,45*mm])]),Spacer(1,3),
 P("<b>Where the model is less certain.</b>",B),
 bl("<b>Small samples.</b> Ashutosh Sharma and Krunal Pandya rest on 116–133 pressure balls over 17–20 matches. Opposition mix matters: Sufiyan Muqeem (dropped by the 15-match rule) took 35% of his pressure balls against Zimbabwe, Oman and A-teams and falls to 15th without those matches. Mohsin Khan (24 matches) stays in the top six in every variant except T20I-only (too few balls), since 2024 (41st) and the non-pressure baseline (10th)."),
 bl("<b>Context-dependent form.</b> Rinku Singh is 2nd–4th in most variants but 21st on T20I-only and 39th since 2024, so his rating is concentrated in some seasons; Rashid Khan's batting rating likewise comes from IPL (60th on T20I-only). Tewatia and Shanaka have wide rank ranges, and Shanaka's rating comes from T20I matches (too few IPL balls to rank on IPL alone)."),
 bl("<b>Win-probability model.</b> It is fitted to 818 matches without team-strength, venue, pitch or dew inputs, and the first-innings model is weaker (64% accuracy), so first-innings pressure is measured less sharply than chase pressure. We measure each bowler's usual level on legal balls only; including wides and no-balls keeps 9 of the ten bowlers (Abrar Ahmed replaces Lockie Ferguson) and predicts held-out pressure value slightly better (0.09 against 0.06), and a per-match rather than pooled pressure cut-off keeps 8 batters (Sooryavanshi and Shashank Singh replace Shreyas Iyer and Tilak Varma) and all 10 bowlers. Rerunning on the original data file, with estimated byes, keeps 7 batters and 8 bowlers (rank correlation 0.96 and 0.98 across all players). A refit on pre-2025 matches scores 2025–26 almost as well (63% and 81% accuracy, against 64% and 82% for the full-data model), and its ratings correlate 0.94 and 0.96 with ours, keeping 8 and 9 of the top ten."),
 bl("<b>No auction context.</b> We have no price, nationality, availability or injury data, so rankings show who performs, not who is a bargain.")]
el+= [P('8. Related work and robustness checks',H1),
 P("Our approach belongs to the family of leverage-weighted and context-adjusted player metrics: Misra and Rajaraman (2026) value each delivery by its leverage and add an iterative opposition adjustment; Bandyopadhyay (2026) rates batting and bowling as runs above a contextual expectation, stabilised by empirical-Bayes shrinkage; Arachchi, Manage and Scariano (2024) define a pressure index for the team batting second in T20Is. We differ in estimating leverage from the supplied data, covering both innings and bowlers, and choosing the shrinkage weight by out-of-sample prediction. We read these papers' abstracts and outlines only and did not run their code; the three checks below are in the same spirit, not replications.",B),
 bl("<b>Iterative opposition adjustment</b> (player-level opponent quality, iterated): nine of ten batters and nine of ten bowlers stay (Tewatia and Mujeeb Ur Rahman slip to 11th; rank correlation 0.99)."),
 bl("<b>Pace/spin and batter-hand baseline:</b> nine batters and eight bowlers stay; Shreyas Iyer slips to 11th, and spinners Mujeeb Ur Rahman and Krunal Pandya drop to 15th and 19th since spinners are now compared with other spinners. We keep the pooled baseline: the question is what a player adds to winning, not how good he is for his type."),
 bl("<b>Ground scoring level:</b> using the venue in matches.csv we grouped grounds into low, medium and high scoring (by shrunk first-innings totals) and compared balls only within a group. The same ten batters and nine of ten bowlers remain (rank correlation 0.96 and 0.97); Mujeeb Ur Rahman drops to 12th."),
 P("References: Misra and Rajaraman, <i>Delta</i> (April 2026, cs.columbia.edu/~misra/delta-2026.pdf); Bandyopadhyay, <i>Context-adjusted Player Evaluation for Twenty20 Cricket</i> (arXiv:2608.18020, 2026); Arachchi, Manage and Scariano, <i>A pressure index for the team batting second in T20I cricket</i> (2024). <b>Reproducibility:</b> all steps are deterministic code on the supplied CSVs (bootstrap seed 42); ratings use the data pack only, and public articles inform only the RR remarks in §6.",CAP)]
def foot(c,d):
    c.saveState(); c.setFont('DV',7); c.setFillColor(colors.HexColor('#777')); c.drawString(16*mm,8*mm,'SupeRR Selector S2 · Round 1 methodology'); c.drawRightString(A4[0]-16*mm,8*mm,f'Page {d.page}'); c.restoreState()
doc.build(el,onFirstPage=foot,onLaterPages=foot)
print('ok')
