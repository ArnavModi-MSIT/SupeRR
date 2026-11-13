# Sensitivity to the estimated bye / leg-bye run values (main: 2.0 / 1.4). The data holds no bye runs.
# Rebuilds prep + win-probability in scratch folders and compares the top ten. Writes bye_sens.json.
import os, sys, json, shutil, subprocess, tempfile
W=os.path.dirname(os.path.abspath(__file__)); DP=os.path.join(W,'..','6af3166e7b922_data_pack')
EV='''
import sys, json
from core import *
b=load('main'); b.attrs={}
res={}
for role,minp in (('bat',100),('bowl',90)):
    main=pd.read_pickle(sys.argv[1]+'/final_'+role+'.pkl').sort_values('rank'); top=list(main.index[:10])
    o=rate(tables(b,role),minp=minp); o=o[(o['last']>='2026-01-01')&(o.matches>=MIN_PRESSURE_MATCHES)]; o['rk']=o.rating.rank(ascending=False)
    r=o.rk.reindex(top); res[role]={'kept':int((r<=10).sum()),'out':[main.name[p] for p in top if not r[p]<=10],'in':[o.name[p] for p in o.index[o.rk<=10] if p not in top]}
print(json.dumps(res))
'''
out={}
for tag,by,lb in (('lo',1.0,1.0),('hi',3.0,2.0)):
    T=tempfile.mkdtemp(prefix='bye_'); os.makedirs(f'{T}/work'); os.symlink(os.path.abspath(DP),f'{T}/6af3166e7b922_data_pack')
    shutil.copy(f'{W}/core.py',f'{T}/work/core.py'); shutil.copy(f'{W}/wp.py',f'{T}/work/wp.py')
    p=open(f'{W}/prep.py').read(); a="np.where(b.extras_type=='byes',2.0,0)+np.where(b.extras_type=='legbyes',1.4,0)"; assert a in p
    open(f'{T}/work/prep.py','w').write(p.replace(a,f"np.where(b.extras_type=='byes',{by},0)+np.where(b.extras_type=='legbyes',{lb},0)"))
    for cmd in (['prep.py','../6af3166e7b922_data_pack','balls.pkl'],['wp.py','.']): subprocess.run([sys.executable]+cmd,cwd=f'{T}/work',check=True,capture_output=True)
    open(f'{T}/ev.py','w').write(EV)
    r=subprocess.run([sys.executable,f'{T}/ev.py',W],cwd=f'{T}/work',env=dict(os.environ,PYTHONPATH=f'{T}/work'),capture_output=True,text=True,check=True)
    out[tag]=json.loads(r.stdout.strip().splitlines()[-1]); shutil.rmtree(T)
json.dump(out,open(f'{W}/bye_sens.json','w'),indent=1); print(json.dumps(out,indent=1))
