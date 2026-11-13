from core import *
pd.set_option('display.width',250)
res={}
for mode in ('main','ven'):
    b=load(mode)
    for role,minp in (('bat',100),('bowl',90)):
        T=tables(b,role); o=rate(T,minp=minp); o=o[o['last']>='2026-01-01']; o['rk']=o.rating.rank(ascending=False); res[(mode,role)]=o
for role in ('bat','bowl'):
    a=res[('main',role)].sort_values('rating',ascending=False); c=res[('ven',role)]
    j=a[['name','v100','rk']].join(c[['v100','rk']],rsuffix='_ven')
    print(role,'spearman',j[['rk','rk_ven']].corr('spearman').iloc[0,1].round(3)); print(j.head(14).round(2).to_string())
    print('ctx top10:',list(c.sort_values('rating',ascending=False).head(10).name))
