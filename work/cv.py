from core import *
b=load('main'); ms=b.match_id.unique()
cs=[0,.05,.1,.2,.3,.5,.75,1.0]
for role in ('bat','bowl'):
    T=tables(b,role); rng=np.random.default_rng(1); acc={c:[] for c in cs}; tail={c:[] for c in cs}
    for i in range(60):
        h=rng.permutation(ms); A=set(h[:len(h)//2]); B=set(h[len(h)//2:])
        a=rate(T,matches=A,minp=30); c_=rate(T,matches=B,minp=30)
        j=a[['pv','prior','n','base']].join(c_[['pv','n']],lsuffix='_a',rsuffix='_b',how='inner')
        w=np.minimum(j.n_a,j.n_b)
        for c in cs:
            pred=j.prior+c*(j.pv_a-j.prior)
            x=pred-np.average(pred,weights=w); y=j.pv_b-np.average(j.pv_b,weights=w)
            acc[c].append((w*x*y).sum()/np.sqrt((w*x*x).sum()*(w*y*y).sum()))
            # top-decile hit: mean realised pv_B of top 15 predicted
            top=pred.sort_values(ascending=False).index[:15]; tail[c].append(j.loc[top,'pv_b'].mean()*100)
    print(role,'weighted corr(pred_A, pv_B):',{c:round(np.mean(v),3) for c,v in acc.items()})
    print(role,'mean realised V/100 balls of top-15 predicted:',{c:round(np.mean(v),3) for c,v in tail.items()})
