# Implementation sensitivity (reviewer-driven): (a) bowler usual-level baseline from ALL deliveries incl. wides/no-balls (main uses legal balls only),
# (b) pressure/ordinary cut-offs computed per match-innings instead of pooled over all first innings / all chases,
# (c) both. Scratch copies of core.py are patched; main outputs are untouched. Writes variant_checks.json.
import os, sys, json, shutil, subprocess, tempfile
W=os.path.dirname(os.path.abspath(__file__)); DP=os.path.join(W,'..','6af3166e7b922_data_pack')
PATCH={
 'bowl_all':[("        d=b[b.legal==1]; pid,nm,V='bowler_id','bowler_name','V_bowl'   # legal balls only, matching pressure/ordinary samples","        d=b; pid,nm,V='bowler_id','bowler_name','V_bowl'")],
 'cut_match':[("    cut=b[b.legal==1].groupby('innings').li.quantile(.8); med=b[b.legal==1].groupby('innings').li.quantile(.5)\n    b['press']=(b.legal==1)&(b.li>=b.innings.map(cut))",
               "    Lg=b[b.legal==1]; cutm=Lg.groupby(['match_id','innings']).li.quantile(.8).rename('cutm'); medm=Lg.groupby(['match_id','innings']).li.quantile(.5).rename('medm')\n    b=b.join(cutm,on=['match_id','innings']).join(medm,on=['match_id','innings'])\n    med=None; b['press']=(b.legal==1)&(b.li>=b.cutm)"),
              ("    b['ordin']=(b.legal==1)&(b.li<b.innings.map(med))","    b['ordin']=(b.legal==1)&(b.li<b.medm)")],
}
PATCH['both']=PATCH['bowl_all']+PATCH['cut_match']
EV='''
import sys, json
from core import *
b=load('main'); b.attrs={}
res={}
for role,minp in (('bat',100),('bowl',90)):
    main=pd.read_pickle(sys.argv[1]+'/final_'+role+'.pkl').sort_values('rank'); top=list(main.index[:10])
    o=rate(tables(b,role),minp=minp); o=o[(o['last']>='2026-01-01')&(o.matches>=MIN_PRESSURE_MATCHES)]; o['rk']=o.rating.rank(ascending=False)
    newtop=list(o.sort_values('rating',ascending=False).index[:10])
    res[role]={'kept':int(sum(1 for p in top if p in newtop)),'out':[main.name[p] for p in top if p not in newtop],'in':[o.name[p] for p in newtop if p not in top],
               'order':[o.name[p] for p in newtop],'eligible':int(len(o)),'press_share':float(b.press.sum()/(b.legal==1).sum())}
print(json.dumps(res))
'''
out={}
for tag,pairs in PATCH.items():
    T=tempfile.mkdtemp(prefix='vc_'); os.makedirs(f'{T}/work'); os.symlink(os.path.abspath(DP),f'{T}/6af3166e7b922_data_pack')
    src=open(f'{W}/core.py').read()
    for a,b_ in pairs:
        assert a in src,(tag,a[:60]); src=src.replace(a,b_)
    open(f'{T}/work/core.py','w').write(src)
    for f in ('balls_wp.pkl',): os.symlink(f'{W}/{f}',f'{T}/work/{f}')
    open(f'{T}/ev.py','w').write(EV)
    r=subprocess.run([sys.executable,f'{T}/ev.py',W],cwd=f'{T}/work',env=dict(os.environ,PYTHONPATH=f'{T}/work'),capture_output=True,text=True)
    if r.returncode: print(tag,r.stderr[-800:]); continue
    out[tag]=json.loads(r.stdout.strip().splitlines()[-1]); shutil.rmtree(T)
json.dump(out,open(f'{W}/variant_checks.json','w'),indent=1); print(json.dumps(out,indent=1))
