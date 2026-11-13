import pandas as pd, numpy as np, os, sys
W=os.path.dirname(os.path.abspath(__file__)); DP=os.path.join(W,'..','6af3166e7b922_data_pack')
b=pd.read_pickle(f'{W}/balls_wp.pkl')
t=pd.read_csv(f'{DP}/teams.csv').drop_duplicates('team_id').set_index('team_id').team_name
b['bat_team']=b.batting_team_id.map(t); b['bowl_team']=b.bowling_team_id.map(t)
FULL={'India','Pakistan','West Indies','New Zealand','Bangladesh','Sri Lanka','England','Afghanistan','Zimbabwe','Australia','South Africa','Ireland'}
ipl_f=(b.ipl==1)&~b.bat_team.str.contains(' A$',regex=True,na=False)&~b.bowl_team.str.contains(' A$',regex=True,na=False)
b['w']=np.where(ipl_f|((b.ipl==0)&b.bat_team.isin(FULL)&b.bowl_team.isin(FULL)),1.0,0.5)
# pressure flag: top-20% leverage within innings (legal balls)
cut=b[b.legal==1].groupby('innings').li.quantile(.8)
b['press']=(b.legal==1)&(b.li>=b.innings.map(cut))
med=b[b.legal==1].groupby('innings').li.quantile(.5)
b['ordin']=(b.legal==1)&(b.li<b.innings.map(med))
MODE=sys.argv[1] if len(sys.argv)>1 else 'main'
if MODE=='abs': b['press']=(b.legal==1)&(b.li>=1.3)
b['date']=pd.to_datetime(b.match_date)
def eb(rate,n,sig2,minn=0):
    # method-of-moments random effects, rate per ball
    mu=np.average(rate,weights=n); v=np.average((rate-mu)**2,weights=n)
    tau2=max(v-np.average(sig2/n,weights=n),1e-12)
    B=tau2/(tau2+sig2/n); return mu+B*(rate-mu),B,tau2
def build(role,minp):
    if role=='bat':
        d=b[b.bat_ok&(b.legal==1)].copy(); pid='striker_id'; nm='striker_name'; V='V_bat'
    else:
        d=b.copy(); pid='bowler_id'; nm='bowler_name'; V='V_bowl'
    d['v']=d[V]
    names=d.groupby(pid)[nm].agg(lambda s:s.mode().iloc[0])
    P=d[d.press]; O=d[d.ordin]
    g=P.groupby(pid)
    out=pd.DataFrame({'name':names})
    out['p_balls']=g.size(); out['p_w']=g.w.sum()
    out['p_v']=g.apply(lambda x:(x.v*x.w).sum()/x.w.sum())
    out['p_var']=g.v.var()
    out['matches']=g.match_id.nunique()
    gO=O.groupby(pid); out['o_balls']=gO.size(); out['o_v']=gO.apply(lambda x:(x.v*x.w).sum()/x.w.sum())
    if role=='bat':
        out['p_runs']=g.bat_runs.sum(); out['p_sr']=out.p_runs/out.p_balls*100
        out['p_dis']=g.apply(lambda x:((x.is_wicket)&(x.dismissed_player_id==x.striker_id)).sum())
        out['p_bpct']=g.apply(lambda x:(x.is_four|x.is_six).mean()*100)
        out['o_sr']=gO.bat_runs.sum()/out.o_balls*100
        out['o_dis']=gO.apply(lambda x:((x.is_wicket)&(x.dismissed_player_id==x.striker_id)).mean())
    else:
        P2=P; g2=P2.groupby(pid)
        out['p_econ']=g2.bowl_runs.sum()/g2.size()*6; out['p_wk']=g2.bowl_wk.sum(); out['p_dot']=g2.apply(lambda x:((x.bowl_runs==0)).mean()*100)
        O2=O.groupby(pid); out['o_econ']=O2.bowl_runs.sum()/O2.size()*6
    out=out[out.p_balls>=minp].copy()
    # sigma2 = pooled per-ball variance
    sig2=np.average(out.p_var,weights=out.p_balls)
    out['v100_raw']=out.p_v*100
    sh,B,tau2=eb(out.p_v.values,out.p_balls.values,sig2)
    out['v100']=sh*100; out['B']=B
    # delta vs own ordinary baseline (shrunk each)
    so=np.average(d[d.ordin].groupby(pid).v.var().dropna()); 
    out['d_raw']=(out.p_v-out.o_v)*100
    # consistency: share of match-samples with net V>0
    ms=P.groupby([pid,'match_id','innings']).agg(v=('v','sum'),n=('v','size'),w=('w','first')).reset_index()
    ms=ms[ms.n>=(3 if role=='bat' else 4)]
    cons=ms.groupby(pid).apply(lambda x:pd.Series({'samples':len(x),'hit':(x.v>0).sum()}))
    out=out.join(cons); out['samples']=out.samples.fillna(0); out['hit']=out.hit.fillna(0)
    out['cons']=(out.hit+4)/(out.samples+8)   # shrink to 50%
    # shrink delta
    sd2=sig2*(1/out.p_balls+1/out.o_balls)*1e4
    dm=np.average(out.d_raw,weights=out.p_balls)
    v=np.average((out.d_raw-dm)**2,weights=out.p_balls); tau=max(v-np.average(sd2,weights=out.p_balls),1e-9)
    out['d_shr']=dm+(tau/(tau+sd2))*(out.d_raw-dm)
    z=lambda s:(s-s.mean())/s.std()
    out['rating']=0.70*z(out.v100)+0.15*z(out.cons)+0.15*z(out.d_shr)
    out=out.sort_values('rating',ascending=False)
    out.attrs['tau2']=tau2; out.attrs['sig2']=sig2
    return out,P,pid
if __name__=='__main__':
    pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
    for role,minp in (('bat',100),('bowl',90)):
        o,P,pid=build(role,minp); print(role,len(o),'tau2',o.attrs['tau2'],'sig2',o.attrs['sig2'])
        cols=['name','p_balls','matches','v100_raw','v100','B','d_shr','cons','samples']+(['p_sr','p_dis','p_bpct','o_sr'] if role=='bat' else ['p_econ','p_wk','p_dot','o_econ'])
        print(o[cols].head(15).round(2).to_string())
        o.to_pickle(f'{W}/rating_{role}_{MODE}.pkl')
