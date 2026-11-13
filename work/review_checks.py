# Checks prompted by external review (13 Nov 2026). Prints how our ten move under each variant.
from core import *
pd.set_option('display.width',250)
b=load('main'); b.attrs={}
comp=b.drop_duplicates('match_id').set_index('match_id')
isipl=comp.comp_name.str.startswith('IPL',na=False).values
t20i=(comp.ipl==0).values; full=(comp.bat_team.isin(FULL)&comp.bowl_team.isin(FULL)).values
cat=pd.Series(np.select([isipl,comp.ipl.values==1,t20i&full,t20i&~full],['IPL','A-team','T20I full-member','T20I associate'],'?'),index=comp.index)
print(cat.value_counts().to_dict())
b['cat']=b.match_id.map(cat)
res={}
def run(role,minp,label,T=None,matches=None,wts=None,minp_v=None):
    T=T or tables(b,role)
    o=rate(T,matches=matches,minp=minp_v or minp); o=o[o.index.isin(elig[role])]
    o['rk']=o.rating.rank(ascending=False); return o
elig={}; top={}; base={}
for role,minp in (('bat',100),('bowl',90)):
    f=pd.read_pickle(f'final_{role}.pkl').sort_values('rank'); elig[role]=set(f.index); top[role]=list(f.index[:10]); base[role]=f
def report(label,role,o):
    t=top[role]; r=o.rk.reindex(t)
    inn=int((r<=10).sum()); gone=[base[role].name[p] for p in t if not r.get(p,np.inf)<=10]
    new=[o.name[p] for p in o.index[o.rk<=10] if p not in t]
    print(f'{label:34s} {role:4s} kept {inn}/10 out:{gone} in:{new}')
# --- variants of the baseline
for role,minp in (('bat',100),('bowl',90)):
    T=tables(b,role)
    d=b[b.bat_ok&(b.legal==1)] if role=='bat' else b
    pid='striker_id' if role=='bat' else 'bowler_id'; V='V_bat' if role=='bat' else 'V_bowl'
    d=d.assign(v=d[V],pid=d[pid],wv=d[V]*d.w)
    TA=d[~d.press].groupby(['pid','match_id','innings']).agg(n=('v','size'),sw=('w','sum'),swv=('wv','sum')).reset_index()
    T1=dict(T); T1['TA']=TA; T1['sig2a']=d[~d.press].v.var()
    o=run(role,minp,'usual excl. pressure balls',T=T1); report('usual excl. pressure balls',role,o)
    if role=='bowl':
        dl=d[d.legal==1]
        TA=dl.groupby(['pid','match_id','innings']).agg(n=('v','size'),sw=('w','sum'),swv=('wv','sum')).reset_index()
        T2=dict(T); T2['TA']=TA; T2['sig2a']=dl.v.var()
        o=run(role,minp,'',T=T2); report('bowler usual level legal balls only',role,o)
        TA=dl[~dl.press].groupby(['pid','match_id','innings']).agg(n=('v','size'),sw=('w','sum'),swv=('wv','sum')).reset_index()
        T3=dict(T); T3['TA']=TA; T3['sig2a']=dl[~dl.press].v.var()
        o=run(role,minp,'',T=T3); report('bowler legal + excl. pressure',role,o)
    # c=0 (pure prior) and lift ranking
    o=rate(T,minp=minp); o=o[o.index.isin(elig[role])]; o['rk']=o.rating.rank(ascending=False)
    o0=o.copy(); o0['rating']=o0.prior; o0['rk']=o0.rating.rank(ascending=False); report('c=0 (prior only, no pressure data)',role,o0)
    o1=o.copy(); o1['rating']=o1.lift; o1['rk']=o1.rating.rank(ascending=False); report('rank by shrunk lift only',role,o1)
    print('   top-10 by lift:',list(o1.sort_values('rk').name.head(10)))
    o2=o.copy(); o2['rating']=o2.pv; o2['rk']=o2.rating.rank(ascending=False); report('raw pressure value only',role,o2)
    # subsets
    sets={'true IPL only':set(cat.index[cat=='IPL']),
          'excl. associates and A-teams':set(cat.index[cat.isin(['IPL','T20I full-member'])]),
          'T20I full-member only':set(cat.index[cat=='T20I full-member'])}
    for k,s in sets.items():
        o=rate(T,matches=s,minp=30); o=o[o.index.isin(elig[role])]; o['rk']=o.rating.rank(ascending=False)
        report(k,role,o)
        if role=='bowl' and k=='excl. associates and A-teams': print('   Muqeem rank',o.rk.get(34485,'below min balls'),'n',o.n.get(34485,np.nan))
    # chase-only pressure
    bb=b.copy(); bb['press']=bb.press&(bb.innings==2)
    Tc=tables(bb,role); o=rate(Tc,minp=60); o=o[o.index.isin(elig[role])]; o['rk']=o.rating.rank(ascending=False); report('pressure = chases only (min 60)',role,o)
    # >=15 pressure matches
    o=rate(T,minp=minp); o=o[o.index.isin(elig[role])&(o.matches>=15)]; o['rk']=o.rating.rank(ascending=False); report('require >=15 pressure matches',role,o)
# composition of pressure balls for our ten
for role,pid in (('bat','striker_id'),('bowl','bowler_id')):
    d=b[b.press&(b.bat_ok if role=='bat' else True)]
    ct=pd.crosstab(d[pid],d.cat,normalize='index').reindex(top[role]).round(2)
    ct.index=[base[role].name[p] for p in ct.index]; print(role,'share of pressure balls by competition type'); print(ct.to_string())
