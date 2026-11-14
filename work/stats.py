from core import *
import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
PINK='#E6007E'; NAVY='#0B1F4B'; GREY='#8A93A6'
b=load('main'); L=b[b.legal==1]; S={}
S['rows']=len(b); S['matches']=b.match_id.nunique(); S['ipl_m']=b[b.ipl==1].match_id.nunique(); S['t20i_m']=b[b.ipl==0].match_id.nunique()
S['balls']=len(L); S['press_balls']=int(L.press.sum()); S['ord_balls']=int(L.ordin.sum())
cut=L.groupby('innings').li.quantile(.8).to_dict(); S['cut']=cut
# profile pressure vs ordinary
def prof(d):
    return dict(share_inn2=(d.innings==2).mean()*100, wk=d.wk_before.mean(), bl=d.bl.mean(), rrr=d[d.innings==2].rrr.clip(0,36).mean(), wpmid=((d.wp_b>.25)&(d.wp_b<.75)).mean()*100,
      pp=(d.overid<=6).mean()*100, mid=((d.overid>6)&(d.overid<=16)).mean()*100, death=(d.overid>16).mean()*100, li=d.li.mean())
S['prof_p']=prof(L[L.press]); S['prof_o']=prof(L[L.ordin]); S['prof_all']=prof(L)
S['runs_per_ball_p']=L[L.press].tot.mean(); S['runs_per_ball_o']=L[L.ordin].tot.mean(); S['wk_p']=L[L.press].wk.mean()*100; S['wk_o']=L[L.ordin].wk.mean()*100
# --- fig1 calibration + LI by over
d2=L[L.innings==2]; q=pd.qcut(d2.wp_b,10,duplicates='drop'); cal=pd.DataFrame({'p':d2.wp_b,'y':d2.bat_win}).groupby(q,observed=True).mean()
d1=L[L.innings==1]; q1=pd.qcut(d1.wp_b,10,duplicates='drop'); cal1=pd.DataFrame({'p':d1.wp_b,'y':d1.bat_win}).groupby(q1,observed=True).mean()
fig,ax=plt.subplots(1,2,figsize=(8,3.1))
ax[0].plot([0,1],[0,1],ls='--',c=GREY,lw=1); ax[0].plot(cal.p,cal.y,'o-',c=PINK,label='2nd innings'); ax[0].plot(cal1.p,cal1.y,'s-',c=NAVY,label='1st innings')
ax[0].set_xlabel('Predicted win probability'); ax[0].set_ylabel('Observed win rate'); ax[0].set_title('Win-probability model calibration',fontsize=9,loc='left'); ax[0].legend(frameon=False)
for inn,c in ((1,NAVY),(2,PINK)):
    g=L[L.innings==inn].groupby('overid').li.mean(); ax[1].plot(g.index,g.values,'o-',c=c,label=f'Innings {inn}',ms=3)
ax[1].axhline(1,c=GREY,ls='--',lw=1); ax[1].set_xlabel('Over'); ax[1].set_ylabel('Mean leverage index'); ax[1].set_title('Leverage (pressure) index by over',fontsize=9,loc='left'); ax[1].legend(frameon=False)
plt.tight_layout(); plt.savefig('fig/fig1.png',dpi=200); plt.close()
S['cal_err2']=float((cal.p-cal.y).abs().mean()); S['cal_err1']=float((cal1.p-cal1.y).abs().mean())
# --- fig2: pressure vs ordinary profile
fig,ax=plt.subplots(1,3,figsize=(8,2.6))
lab=['Ordinary','Pressure']
for a,(k,t) in zip(ax,(('rrr','Mean required rate (chases)'),('wk','Mean wickets down'),('bl','Mean balls remaining'))):
    v=[S['prof_o'][k],S['prof_p'][k]]; a.bar(lab,v,color=[GREY,PINK]); a.set_title(t,fontsize=8.5,loc='left')
    for i,x in enumerate(v): a.text(i,x,f'{x:.1f}',ha='center',va='bottom',fontsize=8)
plt.tight_layout(); plt.savefig('fig/fig2.png',dpi=200); plt.close()
# --- players
role_tabs={}
tops={}
for role in ('bat','bowl'):
    o=pd.read_pickle(f'{W}/final_{role}.pkl').sort_values('rating',ascending=False); top=o.head(10).copy(); tops[role]=top
    # fig3 dotplot
    fig,ax=plt.subplots(figsize=(7,3.4)); y=np.arange(10)[::-1]
    ax.barh(y,top.base100,color=GREY,height=.6,label='Expected from all-ball record')
    ax.barh(y,top.v100-top.base100,left=top.base100,color=PINK,height=.6,label='Pressure-specific lift')
    ax.scatter(top.v100_raw,y,c=NAVY,marker='D',s=18,zorder=5,label='Raw pressure value (unshrunk)')
    ax.set_yticks(y); ax.set_yticklabels([f'{i+1}. {n}' for i,n in enumerate(top.name)]); ax.axvline(0,c='k',lw=.6)
    ax.set_xlabel('Win probability added per 100 pressure balls (wins, vs average player)'); ax.legend(frameon=False,fontsize=7.5,loc='lower right')
    ax.set_title(('Top-10 batters' if role=='bat' else 'Top-10 bowlers')+' under pressure',fontsize=10,loc='left')
    plt.tight_layout(); plt.savefig(f'fig/top_{role}.png',dpi=200); plt.close()
    # fig4 scatter usual vs pressure
    fig,ax=plt.subplots(figsize=(4.6,3.6)); ax.scatter(o.av*100,o.pv*100,s=8,c=GREY,alpha=.6)
    ax.scatter(top.av*100,top.pv*100,s=22,c=PINK)
    for k,(_,r) in enumerate(top.sort_values('rating',ascending=False).iterrows()): ax.annotate(str(k+1),(r.av*100,r.pv*100),fontsize=7,fontweight='bold',color='#0B1F4D',xytext=(4,3),textcoords='offset points')
    lim=[min(o.av.min(),o.pv.min())*100,max(o.av.max(),o.pv.max())*100]; ax.plot(lim,lim,'--',c=GREY,lw=.8)
    ax.set_xlabel('Usual level (all legal balls), wins added per 100 balls'); ax.set_ylabel('Pressure level, wins added per 100 balls'); ax.set_title(('Batters' if role=='bat' else 'Bowlers')+': usual vs pressure level (raw)',fontsize=9,loc='left')
    plt.tight_layout(); plt.savefig(f'fig/scatter_{role}.png',dpi=200); plt.close()
# role descriptors
bb=b.copy()
desc={}
for role in ('bat','bowl'):
    top=tops[role]; pidc='striker_id' if role=='bat' else 'bowler_id'
    for p,r in top.iterrows():
        d=bb[(bb[pidc]==p)]
        P=d[d.press]
        ph=dict(pp=(P.overid<=6).mean()*100,mid=((P.overid>6)&(P.overid<=16)).mean()*100,death=(P.overid>16).mean()*100)
        if role=='bat':
            pv=P[P.bat_ok]; 
            def sr(x): return x.bat_runs.sum()/max(len(x),1)*100
            desc[f'bat{int(p)}']=dict(hand=d.batting_type.mode().iloc[0],order=float(P.batting_order.mean()),inn2=float((pv.innings==2).mean()*100),sr_pace=sr(pv[pv.pace_or_spin=='Pace']),n_pace=int((pv.pace_or_spin=='Pace').sum()),sr_spin=sr(pv[pv.pace_or_spin=='Spin']),n_spin=int((pv.pace_or_spin=='Spin').sum()),**ph,
                 teams=d.bat_team.value_counts().head(2).index.tolist())
        else:
            desc[f'bowl{int(p)}']=dict(btype=d.bowling_type.mode().iloc[0],pace=d.pace_or_spin.mode().iloc[0],inn2=float((P.innings==2).mean()*100),**ph,
                 o_econ=float(d[d.ordin].bowl_runs.mean()*6),teams=d.bowl_team.value_counts().head(2).index.tolist())
S['desc']=desc
for role in ('bat','bowl'):
    top=tops[role]; top.to_csv(f'top_{role}.csv')
json.dump(S,open('stats.json','w',encoding='utf-8'),default=float,indent=1)
print(json.dumps({k:v for k,v in S.items() if k!='desc'},default=float,indent=1)); print(json.dumps(desc,default=float)[:1800])
