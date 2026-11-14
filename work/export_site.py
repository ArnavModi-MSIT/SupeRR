from core import *
import json
S=json.load(open('stats.json',encoding='utf-8'))
b=load('main'); L=b[b.legal==1]
out={'meta':{'matches':S['matches'],'balls':S['balls'],'press_balls':S['press_balls'],'t20i':S['t20i_m'],'ipl':S['ipl_m'],'cut1':S['cut']['1'],'cut2':S['cut']['2'],
 'cal_err2':S['cal_err2'],'cal_err1':S['cal_err1'],'split_bat':0.16,'split_bowl':0.21,'sb_bat':0.28,'sb_bowl':0.34,'c_bat':0.35,'c_bowl':0.10,'data_to':'1 Nov 2026','acc1':0.64,'acc2':0.81,'min_matches':15,'cv0_bat':0.129,'cv_bat':0.138,'cv0_bowl':0.117,'cv_bowl':0.117}}
CONS=json.load(open('consistency.json')); VCK=json.load(open('variant_checks.json'))
# leverage by over + calibration
out['li_over']={str(i):[round(float(x),3) for x in L[L.innings==i].groupby('overid').li.mean().values] for i in (1,2)}
for inn,key in ((2,'cal2'),(1,'cal1')):
    d=L[L.innings==inn]; q=pd.qcut(d.wp_b,10,duplicates='drop'); g=pd.DataFrame({'p':d.wp_b,'y':d.bat_win}).groupby(q,observed=True).mean()
    out[key]=[[round(float(p),3),round(float(y),3)] for p,y in zip(g.p,g.y)]
out['profile']={'ord':S['prof_o'],'press':S['prof_p']}
def blurb(role,p,r):
    d=S['desc'].get(f'{role}{int(p)}')
    if not d: return None
    if role=='bat':
        order=d['order']; rl='powerplay opener' if order<=2.5 else ('top-order / anchor' if order<=4.2 else ('middle-order accelerator' if order<=5.5 else 'late-order finisher'))
        s=f"{d['hand']} {rl} (average pressure position #{order:.1f}). {d['death']:.0f}% of pressure balls come in overs 17–20 and {d['pp']:.0f}% in the powerplay."
        if d['n_spin']>=30 and d['sr_pace']-d['sr_spin']>35: s+=f" Weaker against spin under pressure (strike rate {d['sr_spin']:.0f} vs {d['sr_pace']:.0f} against pace)."
        elif d['n_spin']>=30 and d['sr_spin']>=d['sr_pace']-8: s+=f" Strike rate {d['sr_spin']:.0f} against spin and {d['sr_pace']:.0f} against pace under pressure; no clear weakness by bowling type."
        else: s+=f" Strike rate {d['sr_pace']:.0f} against pace under pressure ({d['n_pace']} balls)."
    else:
        s=f"{d['btype']}. Pressure overs split {d['pp']:.0f}% powerplay, {d['mid']:.0f}% middle, {d['death']:.0f}% death. Economy {r.econ:.2f} under pressure against {d['o_econ']:.2f} in ordinary overs."
    return s
for role in ('bat','bowl'):
    o=pd.read_pickle(f'final_{role}.pkl').sort_values('rating',ascending=False).reset_index()
    rows=[]
    for i,r in o.iterrows():
        row=dict(rank=i+1,id=int(r['pid']),name=r['name'],n=int(r.n),matches=int(r.matches),raw=round(float(r.v100_raw),2),base=round(float(r.base100),2),lift=round(float(r.lift100),2),rating=round(float(r.v100),2),
                 cons=CONS[role]['all'].get(str(int(r['pid']))),ptop=round(float(r.p_top10),2),lo=int(round(r.rank_lo)),hi=int(round(r.rank_hi)),
                 last=str(r['last'])[:10],blurb=blurb(role,r['pid'],r))
        for k in ('rk_abs','rk_top10','rk_noadj','rk_iter','rk_ctx','rk_ven','rk_ipl','rk_t20i','rk_2024p','rk_np','rk_chase','rk_noassoc','rk_iplonly'):
            row[k]=None if pd.isna(r[k]) else int(r[k])
        if role=='bat': row.update(sr=round(float(r.sr),0),bpct=round(float(r.bpct),1),dis=round(float(r.dis_rate),1))
        else: row.update(econ=round(float(r.econ),2),wkts=int(r.wkts),dot=round(float(r.dotpct),0))
        rows.append(row)
    out[role]=rows
top={r:out[r][:10] for r in ('bat','bowl')}
cnt=lambda r,c:sum(1 for x in top[r] if x[c] is not None and x[c]<=10)
out['sens']=[['No opposition-strength correction','rk_noadj'],['Iterative player-level opposition adjustment','rk_iter'],['Baseline by bowler type and batter hand','rk_ctx'],['Baseline by ground scoring level','rk_ven'],['Absolute threshold, leverage ≥ 1.3 (95% chases)','rk_abs'],['Stricter pressure, top 10% leverage','rk_top10'],['T20I matches only','rk_t20i'],['Since 1 Jan 2024 only','rk_2024p'],['Usual level estimated from non-pressure balls only','rk_np'],['Pressure balls from second-innings chases only','rk_chase'],['Excluding Associate-nation and A-team matches','rk_noassoc'],['IPL matches only (true IPL)','rk_iplonly']]
out['sens']=[[n,cnt('bat',c),sum(1 for x in top['bat'] if x[c] is None),cnt('bowl',c),sum(1 for x in top['bowl'] if x[c] is None)] for n,c in out['sens']]
out['sens'].append(['Pressure cut-off set within each match-innings (20% of every match)',VCK['cut_match']['bat']['kept'],0,VCK['cut_match']['bowl']['kept'],0])
out['sens'].append(['Bowler usual level from all deliveries, incl. wides and no-balls',VCK['bowl_all']['bat']['kept'],0,VCK['bowl_all']['bowl']['kept'],0])
open('../docs/data.js','w',encoding='utf-8').write('window.DATA='+json.dumps(out,ensure_ascii=False)+';')
print(len(out['bat']),len(out['bowl']),out['sens'],open('../docs/data.js').__sizeof__())
import os; print(os.path.getsize('../docs/data.js'))
