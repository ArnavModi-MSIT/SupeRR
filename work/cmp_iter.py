from core import *
pd.set_option('display.width',250)
res={}
for mode in ('main','iter'):
    b=load(mode)
    if mode=='iter': print('iter converged in',b.attrs['iter_n'],'delta',b.attrs['iter_delta']); qa=b.attrs['qbat'];qb=b.attrs['qbow']; print('q spread bat sd',qa.std(),'bowl sd',qb.std(),'range',qa.min(),qa.max(),qb.min(),qb.max())
    for role,minp in (('bat',100),('bowl',90)):
        T=tables(b,role); o=rate(T,minp=minp); o=o[o['last']>='2026-01-01']; o['rk']=o.rating.rank(ascending=False)
        res[(mode,role)]=o
for role in ('bat','bowl'):
    a=res[('main',role)].sort_values('rating',ascending=False); c=res[('iter',role)]
    j=a[['name','v100','rk']].join(c[['v100','rk']],rsuffix='_iter')
    print(role,'spearman',j[['rk','rk_iter']].corr('spearman').iloc[0,1].round(3))
    print(j.head(16).round(2).to_string())
    print('iter top10:',list(c.sort_values('rating',ascending=False).head(10).name))
