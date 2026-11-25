import json,pandas as pd
R=json.load(open('output/results.json')); md=open('../README.md').read()
c=pd.read_excel('../data/Fitness_Subscriptions_Dataset.xlsx','customers'); t=pd.read_excel('../data/Fitness_Subscriptions_Dataset.xlsx','transactions')
P=R['pooled_retention']; F=R['forecast']['AAA']; L4=R['ltv_all_2024']; L5=R['ltv_all_2025']
pay=open('output/payback.txt').read()
def m(v,fmt): return fmt.format(v)
checks=[
 (f"{len(c):,}","9,300"),(f"{len(t):,}","64,979"),(f"${c.CAC.min():.2f}","$21.00"),(f"${c.CAC.max():.2f}","$352.46"),(f"${c.CAC.mean():.2f}","$178.92"),
 (f"{(t.Transaction_Type=='Subscription').sum():,}","51,982"),(f"${R['rev_by_type']['Subscription']:,}","$2,006,148"),(f"${R['rev_by_type']['Fitness Challenge']:,}","$178,700"),
 (f"${R['rev_by_type']['Nutrition Plan']:,}","$152,061"),(f"${R['rev_by_type']['Personal Training']:,}","$128,700"),(f"${R['rev_by_type']['Annual Upgrade']:,}","$129,350"),(f"${R['total_rev']:,}","$2,594,959"),
 (str(R['cohort_sizes']['2024-01']),"156"),(str(R['cohort_sizes']['2025-12']),"769"),
 (f"{P['1']}%","84.99%"),(f"{P['2']}%","78.01%"),(f"{P['3']}%","50.01%"),(f"{P['4']}%","47.47%"),(f"{P['6']}%","43.56%"),(f"{P['12']}%","35.73%"),(f"{P['24']}%","29.49%"),
 (f"{R['drop_pp_pooled']['3']:.1f}","28.0"),(f"{R['drop_pp_pooled']['1']:.1f}","15.0"),
 (f"{R['churned_customers']:,}","5,025"),(f"{R['churned_life_counts']['3']:,}","2,188"),(f"{R['churned_life_counts']['1']:,}","1,396"),(f"{R['churned_median_life']:.0f}","3"),
 (str(R['min_max_ret_offset']['3']),"[49.8, 50.3]"),
 (f"${R['monthly_sub_rev']['2024-01']:,}","$6,034"),(f"${R['monthly_sub_rev']['2025-12']:,}","$182,725"),(f"${R['monthly_sub_rev']['2026-01']:,}","$165,465"),
 (f"{R['monthly_sub_rev']['2026-01']-R['monthly_sub_rev']['2025-12']:,}","-17,260"),(f"${R['monthly_sub_rev']['2024-12']:,}","$62,581"),(f"${R['monthly_sub_rev']['2025-01']:,}","$69,267"),
 (f"${F['point']['2026-02-01']:,.0f} ${F['lo']['2026-02-01']:,.0f} ${F['hi']['2026-02-01']:,.0f}","$177,782 $162,679 $193,281"),
 (f"${F['point']['2026-06-01']:,.0f} ${F['lo']['2026-06-01']:,.0f} ${F['hi']['2026-06-01']:,.0f}","$209,698 $179,528 $252,815"),
 (f"${F['point']['2026-12-01']:,.0f} ${F['lo']['2026-12-01']:,.0f} ${F['hi']['2026-12-01']:,.0f}","$255,777 $196,240 $368,914"),
 (f"${F['point']['2027-01-01']:,.0f} ${F['lo']['2027-01-01']:,.0f} ${F['hi']['2027-01-01']:,.0f}","$249,437 $184,857 $377,330"),
 (f"${F['total']:,.0f}","$2,636,681"),
 (f"{L4['customers']:,} ${L4['total_cac']:,.2f} {L4['breakeven_calendar']} ${L4['cum_at_be_cal']:,} ${L4['cum_before_be_cal']:,}","2,816 $501,536.80 2024-12 $528,892 $435,806"),
 (f"{L5['customers']:,} ${L5['total_cac']:,.2f} {L5['breakeven_calendar']} ${L5['cum_at_be_cal']:,} ${L5['cum_before_be_cal']:,}","6,484 $1,162,459.11 2025-12 $1,231,980 $1,010,248"),
 (str(R['avg_cac_by_year']),"{'2024': 178.1, '2025': 179.28}"),
 (f"{R['ltv_sub_2024']['breakeven_calendar']} {R['ltv_sub_2025']['breakeven_calendar']} ${R['ltv_sub_2025']['final_cum']:,}","2025-02 None $1,063,636"),
]
bad=[(a,b) for a,b in checks if a!=b]; print('mismatches:',bad)
for s in ['179.4','178.1','198.83','179.97','3702','131.32']: print(s, s in pay)
for s in ['$179.40','$178.10','$198.83','$179.97','3,702','$131.32','$1,063,636','$1,162,459.11']: assert s in md, s
print('README strings present')
