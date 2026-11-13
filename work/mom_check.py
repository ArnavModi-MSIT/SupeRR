# Sanity check: does our per-ball value pick the official Man of the Match?
import pandas as pd, numpy as np, os
W=os.path.dirname(os.path.abspath(__file__)); DP=os.path.join(W,'..','6af3166e7b922_data_pack')
b=pd.read_pickle(f'{W}/balls_wp.pkl'); m=pd.read_csv(f'{DP}/matches.csv')
m=m[m.man_of_the_match!=0][['match_id','man_of_the_match','win_team_id','comp_id']]
bat=b[b.bat_ok&(b.legal==1)].groupby(['match_id','striker_id']).agg(bv=('V_bat','sum'),runs=('bat_runs','sum')).reset_index().rename(columns={'striker_id':'pid'})
bw=b.groupby(['match_id','bowler_id']).agg(wv=('V_bowl','sum'),wk=('bowl_wk','sum')).reset_index().rename(columns={'bowler_id':'pid'})
t=bat.merge(bw,on=['match_id','pid'],how='outer').fillna(0)
t['val']=t.bv+t.wv; t['naive']=t.runs+20*t.wk; t['rb']=t.runs; t['wb']=t.wk+1e-3*t.wv
t=t[t.match_id.isin(m.match_id)]
mom=m.set_index('match_id').man_of_the_match
t['is_mom']=t.pid==t.match_id.map(mom)
def rankhit(col):
    r=t.groupby('match_id')[col].rank(ascending=False,method='min')
    mr=r[t.is_mom]; mr.index=t.loc[t.is_mom,'match_id']
    return mr
res={}
for c,n in (('val','Our value (batting + bowling)'),('naive','Runs + 20 x wickets'),('rb','Most runs'),('wb','Most wickets')):
    mr=rankhit(c); res[n]=((mr==1).mean(),(mr<=3).mean(),len(mr))
n_in=t.groupby('match_id').pid.nunique().mean()
inmatch=t[t.is_mom].match_id.nunique()
print('matches with MoM',len(m),'MoM appears as batter/bowler in ball data',inmatch,'avg players per match with a ball',round(n_in,1))
for k,v in res.items(): print(f'{k:34s} top1 {v[0]:.3f}  top3 {v[1]:.3f}  (n={v[2]})')
print('random top1 ~',round((1/t.groupby("match_id").pid.nunique()).mean(),3))
# IPL only
ipl=set(pd.read_csv(f'{DP}/competitions.csv').query("comp_name.str.startswith('IPL')",engine='python').comp_id)
mi=m[m.comp_id.isin(ipl)].match_id
for c in ('val','naive'):
    r=t[t.match_id.isin(mi)].copy(); rr=r.groupby('match_id')[c].rank(ascending=False,method='min'); h=rr[r.is_mom]
    print('IPL only',c,'top1',round((h==1).mean(),3),'top3',round((h<=3).mean(),3),'n',len(h))
