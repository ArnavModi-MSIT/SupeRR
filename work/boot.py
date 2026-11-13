from core import *
import sys
pd.set_option('display.width',260); pd.set_option('display.max_columns',40)
b=load('main'); ms=b.match_id.unique(); out={}
for role,minp in (('bat',100),('bowl',90)):
    T=tables(b,role); o=rate(T,minp=minp); o=o[o['last']>='2026-01-01']; elig=set(o.index)
    rng=np.random.default_rng(42); K=300; rk={p:[] for p in elig}
    for i in range(K):
        cnt=pd.Series(rng.multinomial(len(ms),np.ones(len(ms))/len(ms)),index=ms)
        r=rate(T,mult=cnt,minp=minp*0.8); r=r[r.index.isin(elig)]
        ranks=r.rating.rank(ascending=False)
        for p in elig: rk[p].append(ranks.get(p,np.nan))
    R=pd.DataFrame(rk).T
    o['p_top10']=(R<=10).mean(1); o['rank_med']=R.median(1); o['rank_lo']=R.quantile(.1,axis=1); o['rank_hi']=R.quantile(.9,axis=1)
    # sensitivities: rank under alt definitions
    for tag,mode,kw in (('abs','abs',{}),('iter','iter',{}),('ctx','ctx',{}),('ven','ven',{}),('top10','top10',{}),('noadj','noadj',{}),('w05','w05',{})):
        bb=load(mode); TT=tables(bb,role); r=rate(TT,minp=minp); r=r[r.index.isin(elig)]; o['rk_'+tag]=r.rating.rank(ascending=False)
    # ipl-only / t20i-only / recent (2024+)
    for tag,sel in (('ipl',b[b.ipl==1].match_id.unique()),('t20i',b[b.ipl==0].match_id.unique()),('2024p',b[b.date>='2024-01-01'].match_id.unique())):
        r=rate(T,matches=set(sel),minp=30); r=r[r.index.isin(elig)]; o['rk_'+tag]=r.rating.rank(ascending=False)
    o['rank']=o.rating.rank(ascending=False)
    o.to_pickle(f'{W}/final_{role}.pkl')
    cols=['name','n','matches','v100_raw','base100','lift100','v100','cons','p_top10','rank_med','rank_lo','rank_hi','rk_abs','rk_top10','rk_noadj','rk_w05','rk_iter','rk_ctx','rk_ven','rk_ipl','rk_t20i','rk_2024p']
    print(role,len(o)); print(o.sort_values('rating',ascending=False)[cols].head(20).round(2).to_string(),flush=True)
