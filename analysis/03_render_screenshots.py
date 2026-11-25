import os; os.makedirs('./output', exist_ok=True)
import pandas as pd, numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.dates as mdates
A='./output/'; S='../screenshots/'
R=json.load(open(A+'results.json'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
def frame(fig,title,sub):
    fig.patch.set_facecolor('#f3f2f1')
    fig.text(0.015,0.965,title,fontsize=18,weight='bold',color='#252423',va='top')
    fig.text(0.015,0.915,sub,fontsize=10,color='#605e5c',va='top')
    fig.text(0.985,0.012,'Rendered with Python (matplotlib) from the dataset; replace with Power BI screenshot',fontsize=7,color='#8a8886',ha='right')
# 1 cohort
ret=pd.read_csv(A+'retention_matrix.csv',index_col=0)*100
fig=plt.figure(figsize=(20,10.5)); frame(fig,'Customer Cohort','Retention % = customers with a Subscription transaction in month N / customers in cohort (month 0). Rows: Cohort Month (first transaction). Columns: Months Since Cohort.')
ax=fig.add_axes([0.07,0.05,0.9,0.8])
cm=matplotlib.colors.LinearSegmentedColormap.from_list('pb',['#f8696b','#ffeb84','#63be7b'])
ax.imshow(ret.values,cmap=cm,aspect='auto',vmin=25,vmax=100)
for i in range(ret.shape[0]):
    for j in range(ret.shape[1]):
        v=ret.values[i,j]
        if not np.isnan(v): ax.text(j,i,f'{v:.0f}%',ha='center',va='center',fontsize=7)
ax.set_xticks(range(ret.shape[1])); ax.set_xticklabels(range(ret.shape[1]))
ax.set_yticks(range(ret.shape[0])); ax.set_yticklabels([pd.Period(p).strftime('%b %Y') for p in ret.index])
ax.set_xlabel('Months Since Cohort'); ax.set_ylabel('Cohort Month'); ax.xaxis.set_label_position('top'); ax.xaxis.tick_top()
fig.savefig(S+'cohort_analysis.png',dpi=110); plt.close()
# 2 forecast
ms=pd.Series(R['monthly_sub_rev']); ms.index=pd.to_datetime(ms.index)
f=pd.read_csv(A+'forecast_AAA.csv',index_col=0,parse_dates=True)
fig=plt.figure(figsize=(16,8.5)); frame(fig,'Revenue Forecast','Monthly subscription revenue (Transaction_Type = "Subscription") by dim_date[StartOfMonth]. Forecast: 12 months, seasonality 12, 95% CI, ignore last 0 (Holt-Winters additive approximation).')
ax=fig.add_axes([0.07,0.1,0.9,0.72]); ax.set_facecolor('white')
ax.plot(ms.index,ms.values,color='#118dff',lw=2.2,marker='o',ms=3,label='Subscription Revenue (actual)')
fx=[ms.index[-1]]+list(f.index); fy=[ms.values[-1]]+list(f.forecast)
ax.plot(fx,fy,color='#12239e',lw=2,ls='--',label='Forecast')
ax.fill_between(f.index,f.lo95,f.hi95,color='#118dff',alpha=0.15,label='95% confidence interval')
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:f'${v/1000:.0f}K'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.grid(axis='y',color='#e1dfdd'); ax.legend(loc='upper left',frameon=False); ax.set_xlabel('StartOfMonth')
for sp in ['top','right']: ax.spines[sp].set_visible(False)
tot=R['forecast']['AAA']['total']
ax.text(0.99,0.04,f"Forecast Feb 2026 - Jan 2027 total: ${tot:,.0f}",transform=ax.transAxes,ha='right',fontsize=11,weight='bold',color='#12239e')
fig.savefig(S+'revenue_forecast.png',dpi=110); plt.close()
# 3 CAC vs LTV
fig=plt.figure(figsize=(17,8.5)); frame(fig,'CAC vs. LTV','Cumulative LTV (all revenue of the selected cohort-year customers) by StartOfMonth vs Total CAC (constant line). Slicer: Cohort Year = YEAR(customers[Cohort Month]).')
for k,yr in enumerate([2024,2025]):
    ax=fig.add_axes([0.06+k*0.48,0.1,0.42,0.68]); ax.set_facecolor('white')
    cum=pd.read_csv(A+f'cum_ltv_calendar_all_{yr}.csv',index_col=0)['cum_ltv']; cum.index=pd.PeriodIndex(cum.index,freq='M').to_timestamp()
    r=R[f'ltv_all_{yr}']; cac=r['total_cac']
    ax.plot(cum.index,cum.values,color='#118dff',lw=2.2,marker='o',ms=3,label='Cumulative LTV')
    ax.axhline(cac,color='#d64550',ls='--',lw=1.8,label=f'Total CAC ${cac:,.2f}')
    be=pd.Period(r['breakeven_calendar']).to_timestamp()
    ax.scatter([be],[r['cum_at_be_cal']],s=90,color='#e66c37',zorder=5)
    ax.annotate(f"Break-even {be:%b %Y}\nLTV ${r['cum_at_be_cal']:,}",(be,r['cum_at_be_cal']),xytext=((15 if yr==2024 else -150),-45),textcoords='offset points',fontsize=9,arrowprops=dict(arrowstyle='->'))
    ax.set_title(f'Cohort Year = {yr}  ({r["customers"]:,} customers)',loc='left',fontsize=12,weight='bold')
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:f'${v/1e6:.1f}M'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax.grid(axis='y',color='#e1dfdd'); ax.legend(loc='upper left',frameon=False); ax.set_xlabel('StartOfMonth')
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
fig.savefig(S+'cac_vs_ltv.png',dpi=110); plt.close()
# 4 data model
fig=plt.figure(figsize=(14,8)); fig.patch.set_facecolor('#f3f2f1')
fig.text(0.015,0.965,'Data Model',fontsize=18,weight='bold',va='top')
ax=fig.add_axes([0,0,1,0.9]); ax.set_xlim(0,14); ax.set_ylim(0,8); ax.axis('off')
def box(x,y,name,cols,w=3.6):
    h=0.45*len(cols)+0.7
    ax.add_patch(FancyBboxPatch((x,y-h),w,h,boxstyle='round,pad=0.02',fc='white',ec='#605e5c'))
    ax.add_patch(FancyBboxPatch((x,y-0.6),w,0.6,boxstyle='round,pad=0.02',fc='#118dff',ec='#605e5c'))
    ax.text(x+0.15,y-0.3,name,color='white',weight='bold',va='center',fontsize=12)
    for i,cn in enumerate(cols): ax.text(x+0.2,y-0.95-0.45*i,cn,va='center',fontsize=9.5)
    return h
box(0.6,7.4,'customers',['Customer_ID','Subscription_Plan','Country','Acquisition_Channel','CAC','Cohort Month (calc.)','Cohort Year (calc.)'])
box(5.2,7.4,'transactions',['Transaction_ID','Customer_ID','Transaction_Date','Revenue','Transaction_Type','Product','Months Since Cohort (calc.)'])
box(9.8,7.4,'dim_date',['Date','Year','Month Number','Month','StartOfMonth'])
def rel(x1,x2,y,l1,l2):
    ax.annotate('',xy=(x2,y),xytext=(x1,y),arrowprops=dict(arrowstyle='-|>',lw=1.6,color='#252423'))
    ax.text(x1+0.1,y+0.15,l1,fontsize=12,weight='bold'); ax.text(x2-0.35,y+0.15,l2,fontsize=12,weight='bold')
rel(4.2,5.2,6.35,'1','*')
ax.annotate('',xy=(8.8,4.95),xytext=(9.8,4.95),arrowprops=dict(arrowstyle='-|>',lw=1.6,color='#252423'))
ax.text(9.45,5.1,'1',fontsize=12,weight='bold'); ax.text(8.85,5.1,'*',fontsize=12,weight='bold')
ax.text(0.6,2.0,'customers[Customer_ID] 1 -> * transactions[Customer_ID]  (single direction)\ndim_date[Date] 1 -> * transactions[Transaction_Date]  (single direction)\ndim_date = ADDCOLUMNS(CALENDAR(MIN(transactions[Transaction_Date]), MAX(transactions[Transaction_Date])), ...)',fontsize=10.5,family='DejaVu Sans Mono')
fig.text(0.985,0.012,'Rendered with Python (matplotlib); replace with Power BI Model view screenshot',fontsize=7,color='#8a8886',ha='right')
fig.savefig(S+'data_model.png',dpi=110); plt.close()
