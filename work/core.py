import pandas as pd, numpy as np, os, warnings
warnings.filterwarnings('ignore')
W=os.path.dirname(os.path.abspath(__file__)); DP=os.path.join(W,'..','6af3166e7b922_data_pack')
FULL={'India','Pakistan','West Indies','New Zealand','Bangladesh','Sri Lanka','England','Afghanistan','Zimbabwe','Australia','South Africa','Ireland'}
def load(mode='main'):
    b=pd.read_pickle(f'{W}/balls_wp_ctx.pkl' if mode=='ctx' else (f'{W}/balls_wp_ven.pkl' if mode=='ven' else f'{W}/balls_wp.pkl'))
    t=pd.read_csv(f'{DP}/teams.csv').drop_duplicates('team_id').set_index('team_id').team_name
    b['bat_team']=b.batting_team_id.map(t); b['bowl_team']=b.bowling_team_id.map(t)
    isA=lambda s:s.str.contains(' A$',regex=True,na=False)
    ipl_f=(b.ipl==1)&~isA(b.bat_team)&~isA(b.bowl_team)
    b['w']=np.where(ipl_f|((b.ipl==0)&b.bat_team.isin(FULL)&b.bowl_team.isin(FULL)),1.0,0.5)
    if mode!='w05':
        b['w']=1.0
        L=b[b.legal==1]
        sb=L.groupby('bowling_team_id').V_bowl.agg(['mean','size']); sb=sb['mean']*sb['size']/(sb['size']+3000)
        sa=L[L.bat_ok==1].groupby('batting_team_id').V_bat.agg(['mean','size']); sa=sa['mean']*sa['size']/(sa['size']+3000)
        if mode not in ('noadj','iter'):
            b['V_bat']=b.V_bat+b.bowling_team_id.map(sb).fillna(0)     # weak bowling side => V_bat inflated => subtract
            b['V_bowl']=b.V_bowl+b.batting_team_id.map(sa).fillna(0)
        if mode=='iter':
            K=400.0; vb0=b.V_bat.values.copy(); vw0=b.V_bowl.values.copy()
            pb_prior=b.batting_team_id.map(sa).fillna(0).values; pw_prior=b.bowling_team_id.map(sb).fillna(0).values
            opp_bowl_team=b.bowling_team_id.map(sb).fillna(0).values; opp_bat_team=b.batting_team_id.map(sa).fillna(0).values
            legal=(b.legal==1).values; batok=b.bat_ok.values.astype(bool)
            qbat=pd.Series(dtype=float); qbow=pd.Series(dtype=float)
            for it in range(8):
                qb_ball=b.bowler_id.map(qbow).values; qb_ball=np.where(np.isnan(qb_ball),opp_bowl_team,qb_ball)
                qa_ball=b.striker_id.map(qbat).values; qa_ball=np.where(np.isnan(qa_ball),opp_bat_team,qa_ball)
                vb=vb0+qb_ball; vw=vw0+qa_ball
                m1=legal&batok
                d1=pd.DataFrame({'p':b.striker_id.values[m1],'v':vb[m1],'pr':pb_prior[m1]}).groupby('p').agg(n=('v','size'),m=('v','mean'),pr=('pr','mean'))
                qbat_new=d1.pr+d1.n/(d1.n+K)*(d1.m-d1.pr)
                d2=pd.DataFrame({'p':b.bowler_id.values[legal],'v':vw[legal],'pr':pw_prior[legal]}).groupby('p').agg(n=('v','size'),m=('v','mean'),pr=('pr','mean'))
                qbow_new=d2.pr+d2.n/(d2.n+K)*(d2.m-d2.pr)
                delta=max(float((qbat_new-qbat.reindex(qbat_new.index).fillna(0)).abs().max()),float((qbow_new-qbow.reindex(qbow_new.index).fillna(0)).abs().max()))
                qbat,qbow=qbat_new,qbow_new
                if delta<1e-6: break
            b['V_bat']=vb; b['V_bowl']=vw; b.attrs['iter_delta']=delta; b.attrs['iter_n']=it+1
            b.attrs['qbat']=qbat; b.attrs['qbow']=qbow
        b.attrs['sb']=sb; b.attrs['sa']=sa
    cut=b[b.legal==1].groupby('innings').li.quantile(.8); med=b[b.legal==1].groupby('innings').li.quantile(.5)
    b['press']=(b.legal==1)&(b.li>=b.innings.map(cut))
    if mode=='abs': b['press']=(b.legal==1)&(b.li>=1.3)
    if mode=='top10': b['press']=(b.legal==1)&(b.li>=b.innings.map(b[b.legal==1].groupby('innings').li.quantile(.9)))
    b['ordin']=(b.legal==1)&(b.li<b.innings.map(med))
    b['date']=pd.to_datetime(b.match_date)
    b['stk_out']=(b.is_wicket&(b.dismissed_player_id==b.striker_id)).astype(int)
    return b
MIN_PRESSURE_MATCHES=15   # eligibility: pressure balls in at least this many matches
def tables(b,role,usual_np=False):
    if role=='bat':
        d=b[b.bat_ok&(b.legal==1)]; pid,nm,V='striker_id','striker_name','V_bat'
    else:
        d=b[b.legal==1]; pid,nm,V='bowler_id','bowler_name','V_bowl'   # legal balls only, matching pressure/ordinary samples
    d=d.assign(v=d[V],pid=d[pid],wv=d[V]*d.w)
    names=d.groupby('pid')[nm].agg(lambda s:s.mode().iloc[0])
    key=['pid','match_id','innings']
    def agg(x):
        return x.groupby(key).agg(n=('v','size'),sw=('w','sum'),swv=('wv','sum'),sv=('v','sum'),
            runs=('bat_runs' if role=='bat' else 'bowl_runs','sum'),dis=('stk_out' if role=='bat' else 'bowl_wk','sum'),
            bnd=('is_four','sum'),six=('is_six','sum'),dot=('bat_runs' if role=='bat' else 'bowl_runs',lambda s:(s==0).sum())).reset_index()
    du=d[~d.press] if usual_np else d   # usual level: all balls (default) or non-pressure balls only
    TP=agg(d[d.press]); TO=agg(d[d.ordin]); TA=du.groupby(['pid','match_id','innings']).agg(n=('v','size'),sw=('w','sum'),swv=('wv','sum')).reset_index()
    sig2=d[d.press].v.var(); sig2o=d[d.ordin].v.var()
    info=d.groupby('pid').agg(last=('date','max'),first=('date','min'))
    sig2a=du.v.var()
    return dict(TP=TP,TO=TO,TA=TA,sig2a=sig2a,names=names,sig2=sig2,sig2o=sig2o,info=info,role=role)
CW={'bat':0.35,'bowl':0.10}
def rate(T,mult=None,minp=100,matches=None,wts=None,use_delta=True,cw=None):
    TP,TO,TA=T['TP'],T['TO'],T['TA']
    if matches is not None: TP=TP[TP.match_id.isin(matches)]; TO=TO[TO.match_id.isin(matches)]; TA=TA[TA.match_id.isin(matches)]
    if mult is not None:
        TP=TP.assign(m=TP.match_id.map(mult).fillna(0)); TO=TO.assign(m=TO.match_id.map(mult).fillna(0)); TA=TA.assign(m=TA.match_id.map(mult).fillna(0))
    else: TP=TP.assign(m=1.0); TO=TO.assign(m=1.0); TA=TA.assign(m=1.0)
    for c in ('n','sw','swv','runs','dis','bnd','six','dot'): TP[c]=TP[c]*TP.m
    for c in ('n','sw','swv'): TO[c]=TO[c]*TO.m; TA[c]=TA[c]*TA.m
    TP['valid']=(TP.n>0)&(TP.n/TP.m.clip(1e-9)>=(3 if T['role']=='bat' else 4))
    TP['hit']=((TP.sv>0)&TP.valid)*TP.m; TP['vm']=TP.valid*TP.m
    g=TP.groupby('pid').agg(n=('n','sum'),sw=('sw','sum'),swv=('swv','sum'),runs=('runs','sum'),dis=('dis','sum'),bnd=('bnd','sum'),six=('six','sum'),dot=('dot','sum'),hit=('hit','sum'),samp=('vm','sum'),matches=('match_id','nunique'))
    ga=TA.groupby('pid').agg(na=('n','sum'),swa=('sw','sum'),swva=('swv','sum'))
    go=TO.groupby('pid').agg(no=('n','sum'),swo=('sw','sum'),swvo=('swv','sum'))
    o=g.join(go).join(ga).dropna(subset=['n']); o=o[o.n>=minp].copy()
    o['pv']=o.swv/o.sw; o['ov']=(o.swvo/o.swo)
    o['no']=o['no'].fillna(1.0); o['ov']=o['ov'].fillna(o.pv)
    sig2=T['sig2']; n=o.n.values
    mu=np.average(o.pv,weights=n); var=np.average((o.pv-mu)**2,weights=n); tau2=max(var-np.average(sig2/n,weights=n),1e-12)
    Bk=tau2/(tau2+sig2/n); o['B']=Bk; o['v100']=(mu+Bk*(o.pv-mu))*100; o['v100_raw']=o.pv*100
    # hierarchical: usual (all-ball) level -> prior mean for pressure level
    o['av']=o.swva/o.swa; sa=T['sig2a']; na=o.na.values
    mua=np.average(o.av,weights=na); va=np.average((o.av-mua)**2,weights=na); ta=max(va-np.average(sa/na,weights=na),1e-12)
    o['base']=mua+ta/(ta+sa/na)*(o.av-mua)           # shrunk usual level per ball
    X=np.c_[np.ones(len(o)),o.base.values]; Wt=n
    beta=np.linalg.solve((X*Wt[:,None]).T@X,(X*Wt[:,None]).T@o.pv.values)
    o['prior']=X@beta; res=o.pv-o.prior
    tr=max(np.average(res**2,weights=n)-np.average(sig2/n,weights=n),1e-12)
    Br=tr/(tr+sig2/n); o['Br']=Br
    c_=CW[T['role']] if cw is None else cw
    o['post']=o.prior+c_*res; o['lift']=c_*res            # pressure-specific lift
    o['v100']=o.post*100; o['base100']=o.prior*100; o['lift100']=o.lift*100
    o['cons']=(o.hit+4)/(o.samp+8)
    o['d_raw']=(o.pv-o.ov)*100
    sd2=(sig2/o.n+T['sig2o']/o.no)*1e4; dm=np.average(o.d_raw,weights=n)
    vv=np.average((o.d_raw-dm)**2,weights=n); tau=max(vv-np.average(sd2,weights=n),1e-9)
    o['d_shr']=dm+tau/(tau+sd2)*(o.d_raw-dm)
    z=lambda s:(s-s.mean())/s.std()
    a,c,d=wts if wts is not None else (1,0,0)
    o['rating']=o.v100 if wts is None else a*z(o.v100)+c*z(o.cons)+d*z(o.d_shr)
    o['name']=o.index.map(T['names']); o['last']=o.index.map(T['info']['last'])
    if T['role']=='bat':
        o['sr']=o.runs/o.n*100; o['bpct']=(o.bnd+o.six)/o.n*100; o['dis_rate']=o.dis/o.n*100
    else:
        o['econ']=o.runs/o.n*6; o['wkts']=o.dis; o['dotpct']=o['dot']/o.n*100
    o.attrs['tau2']=tau2
    return o.sort_values('rating',ascending=False)
