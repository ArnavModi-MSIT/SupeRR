from core import *
import sys
def split_rel(T,wts,minp=40,N=40,seed=0,ms=None):
    rng=np.random.default_rng(seed); out=[]
    for i in range(N):
        h=rng.permutation(ms); A=set(h[:len(h)//2]); B=set(h[len(h)//2:])
        a=rate(T,matches=A,minp=minp,wts=wts); c=rate(T,matches=B,minp=minp,wts=wts)
        j=a.join(c,lsuffix='_a',rsuffix='_b',how='inner')
        out.append(j[['rating_a','rating_b']].corr('spearman').iloc[0,1])
    return np.mean(out)
for mode in ("main",):
    b=load(mode); ms=b.match_id.unique()
    for role in ('bat','bowl'):
        T=tables(b,role)
        res={w:round(split_rel(T,w,ms=ms,N=30),3) for w in [None]}
        print(mode,role,len(rate(T,minp=100 if role=='bat' else 90)),res,flush=True)
