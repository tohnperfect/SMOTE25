import re,json,pandas as pd,numpy as np
from catalog import key
c=pd.read_json('catalog.json')
c['key2']=c.key.str.replace('vs','')
d=pd.read_csv('/mnt/user-data/uploads/SMOTE25/Data section/out/dataset_records.csv')
d=d[d.is_placeholder=='no'].copy()
def num(x):
    if pd.isna(x): return None
    m=re.search(r'\d[\d,]*',str(x)); 
    return int(m.group().replace(',','')) if m else None
d['pn']=d.n_instances.map(num); d['pf']=d.n_features.map(num); d['pc']=d.n_classes.map(num)
def cands(r):
    ks={key(r.normalized_name),key(r.name_as_reported)}
    m=c[c.key.isin(ks)]
    if m.empty: m=c[c.key2.isin({k.replace('vs','') for k in ks})]
    return m
out=[]
for _,r in d.iterrows():
    m=cands(r); st=None; best=None
    if m.empty: st='no_file'
    elif pd.isna(r.pn): st='file_but_no_printed_size'; best=m.iloc[0]
    else:
        m=m.assign(dn=(m.n-r.pn).abs())
        ex=m[m.dn==0]
        if not ex.empty:
            best=ex.iloc[0]
            if pd.isna(r.pf) or any(abs(int(x)-r.pf)<=0 for x in ex.f.dropna()): st='match_exact'
            elif any(abs(int(x)-r.pf)<=1 for x in ex.f.dropna()): st='match_n_feat_pm1'
            else: st='n_match_feat_diff'
        else:
            best=m.sort_values('dn').iloc[0]
            st='near_<=2pct' if best.dn<=0.02*r.pn else 'size_mismatch'
    out.append(dict(record_id=r.record_id,paper=r.paper_key,name=r.normalized_name,category=r.category,source=r.source_as_reported,
        pn=r.pn,pf=r.pf,status=st,file=None if best is None else best['name'],file_src=None if best is None else best.src,
        file_n=None if best is None else best.n,file_f=None if best is None else best.f))
o=pd.DataFrame(out); o.to_csv('match.csv',index=False)
print(pd.crosstab(o.category,o.status,margins=True).to_string())
