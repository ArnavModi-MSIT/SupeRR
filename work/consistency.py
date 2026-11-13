# Match-to-match consistency: share of a player's pressure matches in which the summed
# pressure value (raw win probability added) is positive. Reads balls_wp.pkl, final_bat/bowl.pkl.
import pandas as pd, numpy as np, json
y=pd.read_pickle('balls_wp.pkl')
fb=pd.read_pickle('final_bat.pkl'); fw=pd.read_pickle('final_bowl.pkl')
cut=np.where(y.innings==1,1.002087830658601,1.592272202481281)
p=y[(y.li>=cut)&(y.legal==1)]
out={}
for role,f,idc,vc,ok in [('bat',fb,'striker_id','V_bat','bat_ok'),('bowl',fw,'bowler_id','V_bowl',None)]:
    q=p[p[ok]] if ok else p
    pm=q.groupby([idc,'match_id'])[vc].sum().reset_index()
    sh=pm.groupby(idc)[vc].apply(lambda s:(s>0).mean())
    cnt=pm.groupby(idc)[vc].size()
    el=sh[sh.index.isin(f.index)]
    top=f.sort_values('rank').head(10)
    t=sh.reindex(top.index)
    out[role]={'top_median':float(t.median()),'top_min':float(t.min()),'top_max':float(t.max()),
               'elig_median':float(el.median()),'by_player':{n:round(float(v),3) for n,v in zip(top.name,t)}}
    print(role,out[role]['top_median'],out[role]['top_min'],out[role]['top_max'],'eligible median',out[role]['elig_median'],len(el))
    print(out[role]['by_player'])
json.dump(out,open('consistency.json','w'),indent=1)
