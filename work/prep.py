import pandas as pd, numpy as np, sys
D=sys.argv[1]; OUT=sys.argv[2]
b=pd.read_csv(f'{D}/ball_by_ball.csv',low_memory=False)
m=pd.read_csv(f'{D}/matches.csv'); c=pd.read_csv(f'{D}/competitions.csv')
m=m.merge(c[['comp_id','match_format','season','comp_name']],on='comp_id',how='left')
# valid matches: full-length, decisive, no DLS
ok=m[m.win_team_id.notna()&m.revised_target.isna()&m.first_inn_revised_overs.isna()&m.second_inn_revised_overs.isna()]
b=b[b.innings.isin([1,2])&b.match_id.isin(ok.match_id)].copy()
b=b.sort_values(['match_id','innings','innings_ball_num']).reset_index(drop=True)
b['legal']=(~b.extras_type.isin(['wide','Overstep','other'])).astype(int)
b['ex']=np.where(b.extras_type.isin(['wide','Overstep']),1,0)+b.extras_2_runs
b['ex']+=np.where(b.extras_type=='byes',2.0,0)+np.where(b.extras_type=='legbyes',1.4,0)+np.where(b.extras_type=='Penalty',5,0)
b['tot']=b.runs+b.ex
b['bat_runs']=np.where(b.extras_type.isin(['byes','legbyes','wide','Penalty']),0,b.runs)
b['wk']=b.is_wicket.astype(int)
g=b.groupby(['match_id','innings'])
b['score_before']=g.tot.cumsum()-b.tot
b['wk_before']=g.wk.cumsum()-b.wk
b['bowled_before']=g.legal.cumsum()-b.legal
b['balls_left']=120-b.bowled_before
inn1=b[b.innings==1].groupby('match_id').tot.sum().rename('inn1_total')
b=b.merge(inn1,on='match_id',how='left')
b['target']=np.where(b.innings==2,b.inn1_total+1,np.nan)
b['need']=b.target-b.score_before
# keep matches where both innings present
cnt=b.groupby('match_id').innings.nunique(); b=b[b.match_id.isin(cnt[cnt==2].index)].copy()
b=b.merge(m[['match_id','match_date','match_format','season','comp_id','comp_name','win_team_id','home_team','away_team']],on='match_id',how='left')
b['bat_win']=(b.win_team_id==b.batting_team_id).astype(int)
b['ipl']=(b.match_format=='T20').astype(int)
b.to_parquet(OUT) if OUT.endswith('.parquet') else b.to_pickle(OUT)
print(b.shape,b.match_id.nunique(), b.groupby('innings').bat_win.mean())
print(b[b.innings==2].groupby('match_id').need.min().describe())
