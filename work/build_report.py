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
H1=ParagraphStyle('h1',fontName='DVB',fontSize=13,textColor=NAVY,spaceBefore=10,spaceAfter=4,keepWithNext=1)
H2=ParagraphStyle('h2',fontName='DVB',fontSize=10,textColor=PINK,spaceBefore=6,spaceAfter=2)
B=ParagraphStyle('b',fontName='DV',fontSize=8.6,leading=12,spaceAfter=4)
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
doc=SimpleDocTemplate('SupeRR_R1_Methodology_Report.pdf',pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=15*mm,bottomMargin=14*mm,title='SupeRR Selector S2 - Round 1 Methodology Report',author='Arnav')
W=A4[0]-32*mm
el=[]
el+= [P('SupeRR Selector Season 2 — Round 1',ParagraphStyle('k',fontName='DVB',fontSize=8,textColor=PINK)),P('Who delivers when the game is on the line?',T),
 P('A leverage-based pressure model for IPL and T20I batters and bowlers, 2022–2026',ParagraphStyle('s',fontName='DV',fontSize=10,textColor=colors.HexColor('#444'),spaceAfter=8))]
el+= [P('1. Summary of approach and results',H1),
 P(f"We define <b>pressure</b> as a delivery whose outcome can swing the match's win probability by an unusually large amount (a <i>leverage index</i>, LI), measured by our own win-probability model fitted on the {S['matches']} complete matches in the data pack. We measure each player's <b>performance under pressure</b> as the win probability they add on those deliveries compared with an average player in the identical situation. Because a pressure sample is small and noisy, each rating blends the player's <b>usual level</b> (all deliveries, shrunk) with a <b>pressure-specific lift</b>; the blend weight was chosen by out-of-sample prediction, not by hand. Rankings use players active in 2026 with enough pressure deliveries, and are stress-tested with 300 match-level bootstraps and ten alternative model definitions or samples."),
 P("<b>Headline finding.</b> Pressure performance is mostly a continuation of general quality: after accounting for a player's usual level, only a modest, batter-specific pressure effect is detectable, and for bowlers it is close to nil. We therefore do not pretend to find hidden 'clutch' specialists; we rank players by their best-supported estimate of how well they will perform when the match is tight.")]
def rank_table(top,role):
    hdr=['#','Player','Press.\nballs','Matches','Raw value\n/100 balls','Usual\nlevel','Rating\n/100 balls','Rank range\n(80% boot.)','P(top 10)']
    rows=[hdr]
    for i,(p,r) in enumerate(top.iterrows(),1):
        rows.append([str(i),r['name'],f"{int(r.n)}",f"{int(r.matches)}",f(r.v100_raw),f(r.base100),f(r.v100),f"{int(round(r.rank_lo))}–{int(round(r.rank_hi))}",f"{r.p_top10*100:.0f}%"])
    return tbl(rows,[7*mm,38*mm,16*mm,16*mm,23*mm,17*mm,20*mm,26*mm,17*mm])
el+= [P('Final top-10 batters under pressure',H2),rank_table(bat,'bat'),Spacer(1,4),P('Final top-10 bowlers under pressure',H2),rank_table(bowl,'bowl'),
 P("Values are win probability added (percentage points) per 100 pressure deliveries relative to an average player in the same situation. 'Raw value' is unshrunk; 'Usual level' is the player's shrunk all-ball value; 'Rating' is what we rank on. Rank ranges come from 300 bootstrap resamples of matches. Rashid Khan appears in both lists, which are ranked independently.",CAP)]
# ---- data
el+= [P('2. Data preparation',H1),
 bl(f"<b>Scope.</b> {S['rows']:,} deliveries from {S['matches']} matches ({S['t20i_m']} T20I and {S['ipl_m']} T20-format matches, i.e. IPL 2022–26 plus a few A-team series), joined to matches, competitions and teams. The data runs to 1 Nov 2026."),
 bl("<b>Excluded for validity.</b> Matches with no result, revised targets or reduced overs (so the required rate is not comparable), single-innings fixtures, and super-over innings: 49 matches in all, leaving 818."),
 bl("<b>Legal balls and extras.</b> Wides, no-balls (including the 'other' type, which are height/full-toss no-balls) do not consume a legal ball. In this file bye and leg-bye runs are not in the <i>runs</i> column, so we reconstruct team scores with calibrated values (≈2.0 per bye, ≈1.4 per leg-bye, found by matching run margins of victory in 393 completed chases), plus 1 per wide/no-ball and any extra penalty runs. This keeps targets and required rates accurate to within a few runs."),
 bl("<b>Attribution.</b> A batter is responsible for runs off the bat and for his own dismissals (non-striker run-outs are not charged to him); wides, no-balls, byes and leg-byes are excluded from his balls faced. A bowler is charged for runs conceded including wides and no-balls but not byes/leg-byes, and credited with wickets other than run-outs and retirements.")]
# ---- pressure
pp,po=S['prof_p'],S['prof_o']
el+= [P('3. How we define pressure',H1),
 P("<b>Step 1 – win probability.</b> For every legal delivery we estimate the batting side's chance of winning from the match state. We first compute the expected runs still to come for a given number of balls left and wickets lost (from the data), then fit a logistic model on that state: in a chase, the gap between the runs required and the expected remaining runs, scaled by the uncertainty remaining; in the first innings, the projected total against the par score. Interactions with balls left and wickets, plus an IPL/T20I indicator, let the same gap matter more late in an innings. The model is well calibrated (mean absolute calibration error "+f"{S['cal_err2']*100:.1f} points in chases, {S['cal_err1']*100:.1f} in first innings; log-loss 0.40 and 0.63; 81% and 64% accuracy)."),
 P("<b>Step 2 – leverage.</b> For each delivery we list the possible outcomes (dot, 1, 2, 3, 4, 6, wicket), weight them by how often each occurs in comparable situations (same innings, phase, wickets down, win-probability band and league), and compute the expected absolute change in win probability. Dividing by the average over all deliveries gives the <b>leverage index</b>: 1.0 is a typical ball, 2.0 means the ball is twice as decisive. Leverage captures every factor the brief lists in one number: required rate, wickets in hand, balls remaining, stage of the innings and how close the contest is."),
 P(f"<b>Step 3 – the pressure threshold.</b> A delivery is a <b>pressure delivery</b> if its leverage is in the top 20% <i>of its own innings</i> (LI ≥ {S['cut']['1']:.2f} in the first innings, ≥ {S['cut']['2']:.2f} in chases). Using each innings' own distribution means batting first and chasing are both represented: first-innings pressure sits mostly in the powerplay (63% of first-innings pressure balls) and the death overs (34%), where wickets and big overs swing the projected total, while chase pressure is a tight equation. This gives {S['press_balls']:,} pressure deliveries. An <b>ordinary delivery</b> is in the bottom half ({S['ord_balls']:,} deliveries) and serves as each player's own baseline."),
 Image('fig/fig1.png',width=W*0.95,height=W*0.95*3.1/8),P("Figure 1. Left: calibration of the win-probability model. Right: mean leverage by over; the last overs of chases are the most decisive.",CAP)]
prof=[['','Ordinary','Pressure'],
 ['Mean leverage index',f(po['li']),f(pp['li'])],['Share of balls with win probability 25–75%',f"{po['wpmid']:.0f}%",f"{pp['wpmid']:.0f}%"],
 ['Powerplay / middle / death share',f"{po['pp']:.0f}% / {po['mid']:.0f}% / {po['death']:.0f}%",f"{pp['pp']:.0f}% / {pp['mid']:.0f}% / {pp['death']:.0f}%"],
 ['Mean balls remaining',f"{po['bl']:.0f}",f"{pp['bl']:.0f}"],['Mean required rate in chases',f"{po['rrr']:.1f}",f"{pp['rrr']:.1f}"],
 ['Wicket probability per ball',f"{S['wk_o']:.1f}%",f"{S['wk_p']:.1f}%"]]
el+= [KeepTogether([tbl(prof,[75*mm,45*mm,45*mm]),P("Table 1. Pressure deliveries are overwhelmingly close-contest situations and over-weight the powerplay and death. They are also more wicket-prone, as expected.",CAP)])]
# ---- performance
el+= [P('4. Measuring performance and setting baselines',H1),
 P("<b>Value of a delivery.</b> For each delivery, <i>value</i> = win probability after what actually happened (from that player's responsibility, see §2) minus the <i>expected</i> win probability after an average delivery in the same situation. This is a win-probability-added measure, but relative to an average player in the same state, so a batter is not rewarded merely for arriving in a favourable state and a bowler is not punished for bowling the 19th over. It is positive for a batter who scores more or loses his wicket less often than average, and for a bowler who concedes less or takes more wickets. It values a wicket by its context (a top-order wicket at 40/3 is worth more than a tail-ender's at 160/8), and a dot ball by how decisive the moment is."),
 P("<b>Player baselines.</b> The brief asks how players perform under pressure <i>compared with their usual levels</i>. For each player we compute (a) <b>usual level</b>: mean value over all their deliveries, and (b) <b>pressure level</b>: mean value over pressure deliveries; their ordinary-ball level is kept for the dip analysis. The ratio between these is the 'dip' or 'rise' under pressure."),
 P("<b>Rating.</b> Pressure samples are small (100–450 balls per player) and win-probability value per ball is very noisy, so raw pressure values are dominated by luck. We use an empirical-Bayes (hierarchical) estimate. The prior for a player's pressure level is a regression on his shrunk usual level; the pressure-specific deviation is then shrunk by a weight <i>c</i>. Rating = usual-level prior + <i>c</i> × (raw pressure level − prior). We chose <i>c</i> by repeated random splits of the matches: predict one half's pressure value from the other half and see which <i>c</i> predicts best. The out-of-sample optimum was <i>c</i> ≈ 0.3–0.5 for batters (we use 0.35) and ≈ 0–0.1 for bowlers (we use 0.10). Batters show a small, real pressure-specific effect; for bowlers the data cannot distinguish pressure skill from general skill, so bowler ratings are mainly about consistent underlying quality in leveraged situations.")]
# ---- fairness
el+= [P('5. Fair comparisons',H1),
 bl("<b>Sample size.</b> Players need ≥ 100 pressure balls faced (batters) or ≥ 90 pressure balls bowled (bowlers). Shrinkage (§4) further pulls small samples toward their expected value. The smallest samples in the final lists are Sufiyan Muqeem (118 balls, 11 matches) and Vaibhav Sooryavanshi (103 balls, 16 matches); both are flagged as less certain in §7."),
 bl("<b>Eligibility for the auction.</b> Only players who appeared in 2026 are ranked (players with no 2026 appearance, such as Dinesh Karthik, Tim Southee and Umesh Yadav, whose last matches in the data are in 2024, are excluded). We cannot see retention lists, so some listed players may already be contracted; this is for RR to verify."),
 bl("<b>IPL vs T20I.</b> We keep both: IPL is the best proxy for auction conditions, while T20I adds volume for overseas players and Associates. The win-probability model and the baselines are league-specific (IPL indicator), so a value is always measured against the same competition's average. Opposition strength is handled with a data-driven correction: each team's mean batting and bowling value is estimated (shrunk with n/(n+3000)), and a bowler's (batter's) value is adjusted by the strength of the batting (bowling) side faced. Corrections are small (up to about ±0.1 points per 100 balls) but push in the expected direction: Zimbabwe, UAE, Oman, Netherlands and A-teams are weakest; India, Australia, England and RCB are strongest. Without this correction, 10/10 batters and 8/10 bowlers stay in the top ten."),
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
    return s
fit_bat={4708:'finisher',8101:'finisher',50284:'opener',6396:'finisher',4904:'middle-order',2436:'finisher',4722:'lower-order hitter',4260:'wicketkeeper-batter, middle order',1699:'top-order stroke-maker',6280:'middle-order'}
el+= [P('6. Evidence for the top 10',H1),
 Image('fig/top_bat.png',width=W*0.9,height=W*0.9*3.4/7),P("Figure 2. Top-10 batters: grey = shrunk usual level; pink = pressure-specific lift added by our model; diamonds = raw pressure value.",CAP),
 Image('fig/top_bowl.png',width=W*0.9,height=W*0.9*3.4/7),P("Figure 3. Top-10 bowlers (same construction).",CAP)]
el+= [P('Batters: what each pick adds',H2)]
for i,(p,r) in enumerate(bat.iterrows(),1):
    el.append(P(f"<b>{i}. {r['name']}</b> — {blurb('bat',p,r,i)}",B))
el+= [P('Bowlers: what each pick adds',H2)]
for i,(p,r) in enumerate(bowl.iterrows(),1):
    el.append(P(f"<b>{i}. {r['name']}</b> — {blurb('bowl',p,r,i)}",B))
el+= [P("Roles come from the ball-by-ball data. <b>RR context (public articles, not the data pack).</b> Previews of IPL 2027 say RR lost Qualifier 2 in 2026, kept changing its bowling unit, and needs finishers, an overseas all-rounder and durable Indian seamers (CricTracker; Mykhel, opinion pieces, not RR statements). The batter list fits the finisher gap (Rinku Singh, Tim David, Ashutosh Sharma, Klaasen); the bowler list fits the need for proven death-overs options (Hazlewood, Bumrah, Ferguson, Muqeem). Sooryavanshi and Shanaka played for RR in 2026, so RR may hold them; Mykhel lists Shanaka as a possible release. <b>Retention check:</b> retentions are due 17 Nov; any of the twenty retained by a club is unavailable at auction, but the performance ranking is unchanged.",CAP)]
el+= [Table([[Image('fig/scatter_bat.png',width=W*0.44,height=W*0.44*3.6/4.6),Image('fig/scatter_bowl.png',width=W*0.44,height=W*0.44*3.6/4.6)]],colWidths=[W*0.5,W*0.5]),
 P("Figure 4. Usual vs pressure level for every qualifying player (grey) and the final top 10 (pink, numbered by final rank). Most players cluster near the diagonal: pressure performance tracks general quality.",CAP)]
# ---- reliability
def cnt(top,c,k=10): return int((top[c]<=k).sum())
rows=[['Alternative definition / sample','Batters still in top 10','Bowlers still in top 10'],
 ['Iterative player-level opposition adjustment (§8)',f"{cnt(bat,'rk_iter')}/10",f"{cnt(bowl,'rk_iter')}/10"],
 ['Baseline by ground scoring level (§8)',f"{cnt(bat,'rk_ven')}/10",f"{cnt(bowl,'rk_ven')}/10"],
 ['Baseline by bowler type (pace/spin) and batter hand',f"{cnt(bat,'rk_ctx')}/10 ({int(bat.rk_ctx.isna().sum())} below min. balls)",f"{cnt(bowl,'rk_ctx')}/10 ({int(bowl.rk_ctx.isna().sum())} below min. balls)"],
 ['No opposition-strength correction',f"{cnt(bat,'rk_noadj')}/10",f"{cnt(bowl,'rk_noadj')}/10"],
 ['Down-weighting Associate/A-team balls by 0.5 instead of the correction',f"{cnt(bat,'rk_w05')}/10",f"{cnt(bowl,'rk_w05')}/10"],
 ['Absolute threshold LI ≥ 1.3 (95% chases)',f"{cnt(bat,'rk_abs')}/10",f"{cnt(bowl,'rk_abs')}/10"],
 ['Stricter pressure (top 10% leverage); smaller samples',f"{cnt(bat,'rk_top10')}/10 ({int(bat.rk_top10.isna().sum())} below min. balls)",f"{cnt(bowl,'rk_top10')}/10 ({int(bowl.rk_top10.isna().sum())} below min. balls)"],
 ['IPL / T20-format matches only',f"{cnt(bat,'rk_ipl')}/10 ({int(bat.rk_ipl.isna().sum())} too few balls)",f"{cnt(bowl,'rk_ipl')}/10 ({int(bowl.rk_ipl.isna().sum())} too few balls)"],
 ['T20I matches only',f"{cnt(bat,'rk_t20i')}/10 ({int(bat.rk_t20i.isna().sum())} too few balls)",f"{cnt(bowl,'rk_t20i')}/10 ({int(bowl.rk_t20i.isna().sum())} too few balls)"],
 ['Since 1 Jan 2024 only',f"{cnt(bat,'rk_2024p')}/10",f"{cnt(bowl,'rk_2024p')}/10"]]
el+= [P('7. Reliability and limitations',H1),
 P("<b>How consistent is the ranking?</b> We tested it four ways."),
 bl("<b>Split-half.</b> Over 30 random halvings of the matches, the rank correlation between ratings from the two halves averaged 0.16 for batters and 0.26 for bowlers (Spearman–Brown corrected to the full sample: about 0.28 and 0.41). Pressure samples are small, so this is modest and we state it plainly."),
 bl("<b>Out-of-sample prediction.</b> Ratings from one half of matches correlate about 0.14 with players' realised pressure value in the other half, higher than the unshrunk pressure values alone (0.13 for batters, 0.09 for bowlers)."),
 bl("<b>Bootstrap.</b> 300 resamples of matches give each player a rank range and a probability of finishing in the top 10 (tables in §1). The leading five or six names in each list are reasonably stable (P(top 10) of roughly 60–90%); places 7–10 are close calls (see P(top 10)). Rinku Singh, Ashutosh Sharma, Vaibhav Sooryavanshi, Tim David and Kamindu Mendis lead the batters; Sufiyan Muqeem, Mohsin Khan, Josh Hazlewood, Varun Chakravarthy, Rashid Khan and Sunil Narine lead the bowlers."),
 bl("<b>Match-to-match consistency.</b> In what share of a player's pressure matches was his pressure value above that of an average player in the same situation? For our top-ten batters the median is 59% (range 44% for Ashutosh Sharma to 100% for Sooryavanshi, over 16 matches), against 54% for all 101 eligible batters; for our top-ten bowlers it is 57% (46% for Varun Chakravarthy to 82% for Muqeem, over 11 matches), against 44% for all 106 eligible bowlers. Ashutosh Sharma's high rating therefore rests on a minority of very good matches, not steady ones."),
 KeepTogether([P("<b>Sensitivity.</b> Number of our ten who stay in the top ten when a modelling choice changes:",B),
 tbl([[Paragraph(str(c),SMW if i==0 else SM) for c in r] for i,r in enumerate(rows)],[88*mm,45*mm,45*mm])]),Spacer(1,3),
 P("<b>Where the model is less certain.</b>",B),
 bl("<b>Small samples.</b> Sufiyan Muqeem and Vaibhav Sooryavanshi rest on 100–120 pressure balls over 11–16 matches. About a third of Muqeem's pressure balls (32%) came against Zimbabwe, Oman and A-teams; the opposition correction is data-driven and small, so his rank is the most sensitive to opposition quality."),
 bl("<b>Context-dependent form.</b> Rinku Singh is first on IPL data but much lower on T20I-only and since-2024 samples, so his lead is concentrated in some seasons. Brook, Kamindu Mendis and Klaasen have wide rank ranges because of 114–169 pressure balls."),
 bl("<b>Dasun Shanaka.</b> His rating is driven by T20I matches; he has too few IPL pressure balls to be ranked on IPL data alone (his IPL 2026 returns in the data are modest: 63 runs at a strike rate of 137)."),
 bl("<b>Role and batting position.</b> A finisher faces the same leverage as an opener, but in fewer, shorter innings, so his value is more variable and we shrink it accordingly. Wicket value comes from our own state-based model, not the game's actual commentary."),
 bl("<b>Win-probability model.</b> It is fitted to 818 matches without team strength, venue, pitch or dew data, and the first-innings model is weaker (64% accuracy), so first-innings pressure is measured less sharply than chase pressure. Byes and leg-byes are estimated."),
 bl("<b>No auction context.</b> We have no price, nationality, availability or injury data, so rankings show who performs, not who is a bargain. Round 2 is the place to combine these.")]
el+= [P('8. Related work and robustness checks',H1),
 P("Our approach belongs to the family of leverage-weighted contribution metrics: Misra and Rajaraman (2026) add an iterative opposition adjustment; Hassan and Rafique (CMSAC 2022) adjust for venue, pace versus spin and handedness; Bandyopadhyay (2026) adjusts expected runs for context, venue and opposition with empirical-Bayes shrinkage; Arachchi, Manage and Scariano (2024) define a pressure index for T20I chases. We differ in estimating leverage from the supplied data, covering both innings and bowlers, and choosing the shrinkage weight by out-of-sample prediction. We summarise these papers only; we did not run their code. Following them we ran three further checks:",B),
 bl("<b>Iterative opposition adjustment</b> (player-level quality of opponents faced, iterated to convergence): the batter list is unchanged; the bowler list has the same ten with two adjacent swaps (Narine/Rashid Khan, Bumrah/Ferguson)."),
 bl("<b>Pace/spin and batter-hand baseline:</b> nine of ten stay in each list. Harry Brook falls below the 100-ball minimum and Kuldeep Yadav slips to 13th, since spinners are now compared with other spinners. We keep the pooled baseline because the question is how much a player adds to winning, not how good he is for his type."),
 bl("<b>Ground scoring level:</b> with no ground field in the data we used the home team as a proxy, grouped grounds into low, medium and high scoring, and compared balls only within a group. The same ten batters and ten bowlers remain (rank correlation 0.95 and 0.97); the proxy is imperfect at neutral venues."),
 P("Delta and a clutch-batting study (South African Statistical Journal, 2021) both report wide uncertainty, and Delta documents sharp regression after breakout bowling seasons; hence our shrinkage and rank ranges.",B)]
el+= [P('9. Reproducibility',H1),
 P("All steps are deterministic code on the supplied CSVs: (1) clean and join, rebuild scores and legal-ball counts; (2) fit the win-probability model (numpy logistic regression with the features in §3); (3) compute leverage and per-ball values; (4) flag pressure and ordinary deliveries; (5) aggregate per player by match, estimate priors and shrinkage; (6) bootstrap and sensitivity runs. Random seeds are fixed (42 for bootstraps). Every rating comes from the data pack alone; public articles inform only the RR remarks in §6.")]
def foot(c,d):
    c.saveState(); c.setFont('DV',7); c.setFillColor(colors.HexColor('#777')); c.drawString(16*mm,8*mm,'SupeRR Selector S2 · Round 1 methodology'); c.drawRightString(A4[0]-16*mm,8*mm,f'Page {d.page}'); c.restoreState()
doc.build(el,onFirstPage=foot,onLaterPages=foot)
print('ok')
