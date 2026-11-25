import os; os.makedirs('./output', exist_ok=True)
import pandas as pd, numpy as np, json, warnings
warnings.filterwarnings('ignore')
X='../data/Fitness_Subscriptions_Dataset.xlsx'
t=pd.read_excel(X,'transactions'); c=pd.read_excel(X,'customers')
t['M']=t.Transaction_Date.dt.to_period('M')
coh=t.groupby('Customer_ID').M.min().rename('Cohort')
c=c.merge(coh,left_on='Customer_ID',right_index=True); c['Year']=c.Cohort.dt.year
t=t.merge(coh,left_on='Customer_ID',right_index=True)
t['Off']=(t.M.dt.year-t.Cohort.dt.year)*12+(t.M.dt.month-t.Cohort.dt.month)
last=pd.Period('2026-01','M')
c['maxoff']=c.Cohort.apply(lambda p:(last.year-p.year)*12+last.month-p.month)
out={}
for yr in [2024,2025]:
  cc=c[c.Year==yr]; rows=[]
  rev=t[t.Customer_ID.isin(cc.Customer_ID)].pivot_table(index='Customer_ID',columns='Off',values='Revenue',aggfunc='sum').reindex(cc.Customer_ID).fillna(0)
  cum=rev.cumsum(axis=1)
  for k in range(0,int(cc.maxoff.max())+1):
    obs=cc[cc.maxoff>=k]
    rows.append((k,len(obs),round(cum.loc[obs.Customer_ID,k].mean(),2),round(obs.CAC.mean(),2)))
  df=pd.DataFrame(rows,columns=['offset','n_obs','avg_cum_ltv','avg_cac'])
  be=df[df.avg_cum_ltv>=df.avg_cac]
  out[yr]=dict(be_offset=int(be.offset.iloc[0]) if len(be) else None, table=df.head(10).values.tolist())
print(json.dumps(out,indent=0))
# seasonal components AAA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
s=t[t.Transaction_Type=='Subscription'].groupby('M').Revenue.sum().astype(float); s.index=s.index.to_timestamp(); s.index.freq='MS'
m=ExponentialSmoothing(s,trend='add',seasonal='add',seasonal_periods=12,initialization_method='estimated').fit()
print(np.round(m.params['initial_seasons'],0))
nons=t[t.Transaction_Type!='Subscription'].groupby(['M','Transaction_Type']).Revenue.sum().unstack(); print(nons.to_string())
print(t[t.M=='2026-01'].groupby('Off').size().tail(3))
