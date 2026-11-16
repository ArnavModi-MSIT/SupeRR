import pandas as pd, numpy as np, sys, pickle
W=sys.argv[1]
b=pd.read_pickle(f'{W}/balls.pkl')
b['fut']=0.0
tot=b.groupby(['match_id','innings']).tot.transform('sum')
b['fut']=tot-b.score_before
b['bl']=b.balls_left.clip(0,120)
# ---- expected remaining runs table R(bl,wk)
L=b[b.legal==1]
BW=6
L=L.assign(blb=(L.bl//BW).clip(0,19),wkc=L.wk_before.clip(0,9))
tab=L.groupby(['blb','wkc']).fut.agg(['mean','count']).reset_index()
R=np.full((20,10),np.nan)
for _,r in tab.iterrows(): R[int(r.blb),int(r.wkc)]=r['mean'] if r['count']>=40 else np.nan
for w in range(10):
    for k in range(20):
        if np.isnan(R[k,w]): R[k,w]=(R[k,w-1]*0.75 if w>0 else R[k-1,w]) if not (k==0) else 0.0
# monotone-ish smoothing in bl
from numpy import interp
centers=np.arange(20)*BW+BW/2
def Rf(bl,wk):
    bl=np.asarray(bl,float); wk=np.clip(np.asarray(wk).astype(int),0,9)
    out=np.empty(bl.shape)
    for w in range(10):
        mk=wk==w
        if mk.any(): out[mk]=interp(bl[mk],centers,R[:,w])
    out=np.where(bl<=0,0.0,out)
    return out
sd_tab=L.groupby('blb').fut.std().values
def sdf(bl): return np.interp(np.asarray(bl,float),centers,sd_tab)
par1=b[b.innings==1].groupby('ipl').tot.sum()/b[b.innings==1].groupby('ipl').match_id.nunique()
par1=par1.to_dict(); print('par',par1,'R(120,0)',Rf([120],[0]))
def feats(inn,score,wk,bl,need,ipl):
    inn=np.asarray(inn); bl=np.asarray(bl,float); wk=np.asarray(wk)
    r=Rf(bl,wk)
    s=np.maximum(sdf(bl),1.0)
    z=np.where(inn==2,(need-r)/np.maximum(s,3.0),0.0)   # >0 => chasing side behind
    z=np.where(inn==2,-z, ((score+r)-np.where(ipl==1,par1[1],par1[0]))/np.sqrt(s**2+25**2))
    z=np.clip(z,-6,6); f=bl/120; w=np.asarray(wk)/10; ipl=np.asarray(ipl,float)
    X=np.c_[np.ones(len(z)),z,z*np.abs(z),f,z*f,w,z*w,ipl,z*ipl]
    return X
def fit(X,y,it=40,lam=1e-3):
    th=np.zeros(X.shape[1])
    for _ in range(it):
        p=1/(1+np.exp(-X@th)); Wd=p*(1-p)+1e-9
        H=(X*Wd[:,None]).T@X+lam*np.eye(X.shape[1]); g=X.T@(y-p)-lam*th
        d=np.linalg.solve(H,g); th+=d
        if np.abs(d).max()<1e-7: break
    return th
models={}
for inn in (1,2):
    d=b[(b.innings==inn)&(b.legal==1)]
    X=feats(d.innings.values,d.score_before.values,d.wk_before.values,d.bl.values,d.need.values,d.ipl.values)
    models[inn]=fit(X,d.bat_win.values.astype(float))
    p=1/(1+np.exp(-X@models[inn])); y=d.bat_win.values
    print(inn,'logloss',-np.mean(y*np.log(p)+(1-y)*np.log(1-p)),'acc',np.mean((p>.5)==y),'theta',np.round(models[inn],2))
def WP(inn,score,wk,bl,need,ipl):
    inn=np.asarray(inn); score=np.asarray(score,float); wk=np.asarray(wk); bl=np.asarray(bl,float); need=np.asarray(need,float); ipl=np.asarray(ipl)
    out=np.zeros(len(inn))
    for i in (1,2):
        mk=inn==i
        if mk.any():
            X=feats(inn[mk],score[mk],wk[mk],bl[mk],need[mk],ipl[mk]); out[mk]=1/(1+np.exp(-X@models[i]))
    m2=inn==2
    out=np.where(m2&(need<=0),1.0,out)
    out=np.where(m2&(need>0)&((wk>=10)|(bl<=0)),np.where(need==1,0.5,0.0),out)
    return np.clip(out,0.0005,0.9995)
# --- calibration check inn2
d=b[(b.innings==2)&(b.legal==1)]
wp=WP(d.innings.values,d.score_before.values,d.wk_before.values,d.bl.values,d.need.values,d.ipl.values)
q=pd.qcut(wp,10,duplicates='drop'); print(pd.DataFrame({'p':wp,'y':d.bat_win.values}).groupby(q,observed=True).mean().round(3))
# ---- ball-level
b['wp_b']=WP(b.innings.values,b.score_before.values,b.wk_before.values,b.bl.values,b.need.values,b.ipl.values)
# outcome probs by bucket
b['phase']=pd.cut(b.overid,[0,6,12,16,20],labels=False)
b['wkb']=pd.cut(b.wk_before,[-1,2,5,10],labels=False)
b['wpb']=pd.cut(b.wp_b,[0,.3,.7,1],labels=False)
bat_ok=(b.legal==1)&(~b.extras_type.isin(['byes','legbyes']))
def outc(df):
    o=np.where(df.dismissed_player_id.eq(df.striker_id),7,df.bat_runs.astype(int).map({0:0,1:1,2:2,3:3,4:4,5:2,6:5,7:5}).fillna(0).astype(int))
    return o
RUNS=np.array([0,1,2,3,4,6,0]);WK=np.array([0,0,0,0,0,0,1])
b['o']=-1
cl=b[bat_ok]
oc=np.where(cl.is_wicket&cl.dismissed_player_id.eq(cl.striker_id),6,cl.bat_runs.map({0:0,1:1,2:2,3:3,4:4,5:2,6:5}).fillna(0).astype(int))
b.loc[cl.index,'o']=oc
m=b.groupby('match_id').agg(t=('inn1_total','first'),h=('venue_id','first'),ipl=('ipl','first')).reset_index()
m['lg']=m.groupby('ipl').t.transform('mean')
g=m.groupby(['ipl','h']).agg(d=('t',lambda x:0),n=('t','size'),mt=('t','mean'),lg=('lg','first')).reset_index()
g['f']=(g.mt-g.lg)*g.n/(g.n+8)
g['vt']=pd.qcut(g.f.rank(method='first'),3,labels=[0,1,2]).astype(int)
b['vt']=b[['ipl','venue_id']].merge(g[['ipl','h','vt']].rename(columns={'h':'venue_id'}),on=['ipl','venue_id'],how='left').vt.fillna(1).astype(int).values
print(g.sort_values('f').head(4)[['ipl','h','n','f']].to_string()); print(g.sort_values('f').tail(4)[['ipl','h','n','f']].to_string())
keys=['innings','phase','wkb','wpb','ipl','vt']
P=pd.crosstab([b.loc[cl.index,k] for k in keys],b.loc[cl.index,'o'])
P=P.reindex(columns=range(7),fill_value=0); P=(P.add(0.5)).div(P.add(0.5).sum(1),axis=0)
Pm=b[keys].merge(P.reset_index(),on=keys,how='left')[list(range(7))].values
Pm=np.where(np.isnan(Pm),np.nanmean(Pm,0),Pm)
n=len(b); Ewp=np.zeros(n); li=np.zeros(n); WPo=[]
for k in range(7):
    wp_k=WP(b.innings.values,b.score_before.values+RUNS[k],b.wk_before.values+WK[k],b.bl.values-1,b.need.values-RUNS[k],b.ipl.values)
    WPo.append(wp_k); Ewp+=Pm[:,k]*wp_k; li+=Pm[:,k]*np.abs(wp_k-b.wp_b.values)
b['E_after']=Ewp; b['li_raw']=li
legal=b.legal==1
b['li']=b.li_raw/b.loc[legal,'li_raw'].mean()
# ---- actual after-state under views
def after(score_add,wk_add,legal_flag):
    return WP(b.innings.values,b.score_before.values+score_add,b.wk_before.values+wk_add,b.bl.values-legal_flag,b.need.values-score_add,b.ipl.values)
# team (actual)
b['wp_a']=after(b.tot.values,b.wk.values,b.legal.values)
# batter view
bstk=(b.is_wicket&b.dismissed_player_id.eq(b.striker_id)).astype(int).values
b['wp_bat']=after(b.bat_runs.values,bstk,b.legal.values)
b['bat_ok']=bat_ok.values
# bowler view: credited wicket
cred=b.is_wicket&~b.dismissal_type.isin(['RunOut','Retire Out','Obstracting the field','Obstructing the field'])
bruns=(b.tot-np.where(b.extras_type.isin(['byes','legbyes']),b.ex,0)).values
b['wp_bowl']=after(bruns,cred.astype(int).values,b.legal.values)
b['bowl_wk']=cred.astype(int)
b['bowl_runs']=bruns
b['V_bat']=b.wp_bat-b.E_after      # batting-team perspective vs average ball
b['V_bowl']=-(b.wp_bowl-b.E_after)
b['rrr']=np.where(b.innings==2,b.need*6/b.bl.clip(1),np.nan)
b.to_pickle(f'{W}/balls_wp_ven.pkl')
print(b[legal].li.describe(percentiles=[.5,.75,.8,.9,.95]))
print(b[legal].groupby('phase').li.mean(), b[legal].groupby('innings').li.mean())
print('Vbat mean (legal ok)',b[b.bat_ok&legal].V_bat.mean(),'Vbowl mean',b[legal].V_bowl.mean(),'illegal Vbowl',b[~legal].V_bowl.mean())
