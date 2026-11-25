import os; os.makedirs('./output', exist_ok=True)
import pandas as pd, numpy as np, json, warnings
warnings.filterwarnings('ignore')
X='../data/Fitness_Subscriptions_Dataset.xlsx'
t=pd.read_excel(X,'transactions'); c=pd.read_excel(X,'customers')
t['M']=t.Transaction_Date.dt.to_period('M')
coh=t.groupby('Customer_ID').M.min().rename('Cohort')
c=c.merge(coh,left_on='Customer_ID',right_index=True)
t=t.merge(coh,left_on='Customer_ID',right_index=True)
t['Off']=(t.M.dt.year-t.Cohort.dt.year)*12+(t.M.dt.month-t.Cohort.dt.month)
s=t[t.Transaction_Type=='Subscription']
R={}
# cohort matrix
act=s.groupby(['Cohort','Off']).Customer_ID.nunique().unstack()
size=act[0]
ret=act.div(size,axis=0)
ret.to_csv('./output/retention_matrix.csv')
act.to_csv('./output/active_customers_matrix.csv')
# pooled retention by offset (only cohorts observed at that offset)
pooled=act.sum()/ [size[act[k].notna()].sum() for k in act.columns]
avg=ret.mean()
R['cohort_sizes']={str(k):int(v) for k,v in size.items()}
R['pooled_retention']={int(k):round(float(v)*100,2) for k,v in pooled.items()}
R['mean_cohort_retention']={int(k):round(float(v)*100,2) for k,v in avg.items()}
R['drop_pp_pooled']={int(k):round(float(pooled[k-1]-pooled[k])*100,2) for k in list(pooled.index)[1:]}
# per-cohort biggest drop
bd={}
for co,row in ret.iterrows():
    r=row.dropna(); d=(r.shift(1)-r).dropna()
    if len(d): bd[str(co)]=int(d.idxmax())
R['biggest_drop_offset_by_cohort_counts']=pd.Series(bd).value_counts().to_dict()
R['min_max_ret_offset']={k:[round(float(ret[k].min())*100,1),round(float(ret[k].max())*100,1)] for k in range(0,5)}
# lifetimes (number of subscription months) for customers
life=s.groupby('Customer_ID').M.nunique(); last=s.groupby('Customer_ID').M.max()
churned=life[last<pd.Period('2026-01','M')]
R['churned_customers']=int(len(churned)); R['active_jan2026']=int((last==pd.Period('2026-01','M')).sum())
R['churned_life_counts']=churned.value_counts().sort_index().head(6).to_dict()
R['churned_median_life']=float(churned.median())
# monthly revenue
ms=s.groupby('M').Revenue.sum(); ma=t.groupby('M').Revenue.sum()
R['monthly_sub_rev']={str(k):int(v) for k,v in ms.items()}
R['monthly_total_rev']={str(k):int(v) for k,v in ma.items()}
R['sub_rev_total']=int(ms.sum()); R['total_rev']=int(ma.sum())
R['rev_by_type']=t.groupby('Transaction_Type').Revenue.sum().astype(int).to_dict()
# forecast
from statsmodels.tsa.holtwinters import ExponentialSmoothing
y=ms.astype(float); y.index=y.index.to_timestamp()
y.index.freq='MS'
fc={}
for name,kw in {'AAA':dict(trend='add',seasonal='add'),'AAN':dict(trend='add',seasonal=None)}.items():
    m=ExponentialSmoothing(y,seasonal_periods=12,initialization_method='estimated',**kw).fit(optimized=True)
    f=m.forecast(12)
    sims=m.simulate(12,repetitions=5000,error='add',random_errors='bootstrap',anchor='end',random_state=42)
    lo=sims.quantile(0.025,axis=1); hi=sims.quantile(0.975,axis=1)
    fc[name]=dict(point={str(k.date()):round(float(v),0) for k,v in f.items()},lo={str(k.date()):round(float(v),0) for k,v in lo.items()},hi={str(k.date()):round(float(v),0) for k,v in hi.items()},total=round(float(f.sum()),0),aic=round(float(m.aic),2),sse=round(float(m.sse),0),params={k:(float(v) if np.isscalar(v) else None) for k,v in m.params.items() if np.isscalar(v)})
    pd.DataFrame({'forecast':f,'lo95':lo,'hi95':hi}).to_csv(f'./output/forecast_{name}.csv')
R['forecast']=fc
# CAC vs LTV
c['Year']=c.Cohort.dt.year
for rev_name,tt in {'all':t,'sub':s}.items():
  for yr in [2024,2025]:
    ids=set(c.Customer_ID[c.Year==yr]); cac=float(c.CAC[c.Year==yr].sum())
    sub=tt[tt.Customer_ID.isin(ids)]
    cal=sub.groupby('M').Revenue.sum().cumsum()
    be_cal=cal[cal>=cac]
    off=sub.groupby('Off').Revenue.sum().cumsum()
    be_off=off[off>=cac]
    R[f'ltv_{rev_name}_{yr}']=dict(customers=len(ids),total_cac=round(cac,2),
        breakeven_calendar=str(be_cal.index[0]) if len(be_cal) else None,
        cum_at_be_cal=int(be_cal.iloc[0]) if len(be_cal) else None,
        cum_before_be_cal=int(cal[cal<cac].iloc[-1]) if len(be_cal) and (cal<cac).any() else None,
        final_cum=int(cal.iloc[-1]),
        breakeven_offset=int(be_off.index[0]) if len(be_off) else None,
        cum_at_be_off=int(be_off.iloc[0]) if len(be_off) else None,
        max_offset=int(off.index.max()))
    pd.DataFrame({'cum_ltv':cal}).to_csv(f'./output/cum_ltv_calendar_{rev_name}_{yr}.csv')
    pd.DataFrame({'cum_ltv':off}).to_csv(f'./output/cum_ltv_offset_{rev_name}_{yr}.csv')
R['total_cac_all']=round(float(c.CAC.sum()),2)
R['avg_cac_by_year']=c.groupby('Year').CAC.mean().round(2).to_dict()
# per-customer avg payback: months of revenue needed (avg)
json.dump(R,open('./output/results.json','w'),indent=1,default=str)
print(json.dumps({k:v for k,v in R.items() if k not in('monthly_total_rev',)},indent=1,default=str))
