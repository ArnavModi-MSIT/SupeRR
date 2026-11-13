# Sensitivity: rank by a conservative lower bound (rating - 0.842*SE, the 20th percentile) instead of the rating
from core import *
import sys
K=int(sys.argv[2]) if len(sys.argv)>2 else 300; role,minp=(('bat',100),('bowl',90))[0 if sys.argv[1]=='bat' else 1]
b=load('main'); ms=b.match_id.unique()
T=tables(b,role); o=rate(T,minp=minp); o=o[(o['last']>='2026-01-01')&(o.matches>=MIN_PRESSURE_MATCHES)]; elig=list(o.index)
rng=np.random.default_rng(42); S=[]
for i in range(K):
    cnt=pd.Series(rng.multinomial(len(ms),np.ones(len(ms))/len(ms)),index=ms)
    r=rate(T,mult=cnt,minp=minp*0.8); S.append(r.rating.reindex(elig))
S=pd.DataFrame(S); o['se']=S.std(); o['lb']=o.rating-0.842*o.se
o['rank_lb']=o.lb.rank(ascending=False); o['rank']=o.rating.rank(ascending=False)
t=o.sort_values('lb',ascending=False)[['name','rating','se','lb','rank','rank_lb']].head(14).round(2)
print(role,'K=',K); print(t.to_string())
top_r=set(o[o['rank']<=10].index); top_l=set(o[o.rank_lb<=10].index); print('overlap with main top10:',len(top_r&top_l),'of 10')
print('main top10 now at rank_lb:',o[o['rank']<=10].sort_values('rank')[['name','rank_lb']].values.tolist())
o[['name','rating','se','lb','rank','rank_lb']].to_pickle(f'lb_{role}.pkl')
