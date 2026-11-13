# Out-of-sample check of the win-probability model: refit using matches before 2025 only, score 2025-26,
# then compare ratings built from 2025-26 matches under the in-sample and out-of-sample models.
# Works in a scratch folder; does not touch the main outputs. Writes oos_check.json.
import os, sys, json, shutil, subprocess, tempfile
W=os.path.dirname(os.path.abspath(__file__)); DP=os.path.join(W,'..','6af3166e7b922_data_pack')
T=tempfile.mkdtemp(prefix='oos_'); os.makedirs(f'{T}/work')
os.symlink(os.path.abspath(DP),f'{T}/6af3166e7b922_data_pack'); os.symlink(f'{W}/balls.pkl',f'{T}/work/balls.pkl'); shutil.copy(f'{W}/core.py',f'{T}/work/core.py')
src=open(f'{W}/wp.py').read()
def rep(a,b):
    global src; assert a in src,a; src=src.replace(a,b)
rep("L=b[b.legal==1]\nBW=6","tr=(pd.to_datetime(b.match_date)<'2025-01-01').values\nL=b[(b.legal==1)&tr]\nBW=6")
rep("par1=b[b.innings==1].groupby('ipl').tot.sum()/b[b.innings==1].groupby('ipl').match_id.nunique()","bt=b[tr]\npar1=bt[bt.innings==1].groupby('ipl').tot.sum()/bt[bt.innings==1].groupby('ipl').match_id.nunique()")
rep("    d=b[(b.innings==inn)&(b.legal==1)]\n    X=feats","    d=b[(b.innings==inn)&(b.legal==1)&tr]\n    X=feats")
rep("cl=b[bat_ok]","cl=b[bat_ok&tr]")
rep("b['li']=b.li_raw/b.loc[legal,'li_raw'].mean()","b['li']=b.li_raw/b.loc[legal&tr,'li_raw'].mean()")
open(f'{T}/work/wp_oos.py','w').write(src)
subprocess.run([sys.executable,'wp_oos.py','.'],cwd=f'{T}/work',check=True,capture_output=True)
EV='''
import sys
from core import *
b=load('main'); b.attrs={}
test=pd.to_datetime(b.match_date)>='2025-01-01'; ms=set(b.match_id[test]); L=b[(b.legal==1)&test]; out={}
for inn in (1,2):
    d=L[L.innings==inn]; p=d.wp_b.clip(1e-4,1-1e-4); y=d.bat_win
    out['ll%d'%inn]=float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p))); out['acc%d'%inn]=float(np.mean((p>.5)==y))
out['test_matches']=len(ms)
for role in ('bat','bowl'):
    o=rate(tables(b,role),matches=ms,minp=30); o=o[o['last']>='2026-01-01']; o[['name','rating']].to_pickle(sys.argv[1]+'_'+role+'.pkl')
import json; print(json.dumps(out))
'''
res={}
for tag,d in (('in',W),('oos',f'{T}/work')):
    open(f'{T}/ev.py','w').write(EV)
    env=dict(os.environ,PYTHONPATH=d)
    r=subprocess.run([sys.executable,f'{T}/ev.py',f'{T}/{tag}'],cwd=d,env=env,capture_output=True,text=True,check=True)
    res[tag]=json.loads(r.stdout.strip().splitlines()[-1])
import pandas as pd
for role in ('bat','bowl'):
    a=pd.read_pickle(f'{T}/in_{role}.pkl'); b=pd.read_pickle(f'{T}/oos_{role}.pkl'); j=a.join(b,lsuffix='_in',rsuffix='_oos',how='inner')
    ra=j.rating_in.rank(ascending=False); rb=j.rating_oos.rank(ascending=False)
    res[role]={'players':len(j),'spearman':float(j[['rating_in','rating_oos']].corr('spearman').iloc[0,1]),'top10_overlap':len(set(ra[ra<=10].index)&set(rb[rb<=10].index))}
json.dump(res,open(f'{W}/oos_check.json','w'),indent=1); print(json.dumps(res,indent=1)); shutil.rmtree(T)
