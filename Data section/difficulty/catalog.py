import os,re,glob,json,pandas as pd
def key(s):
    s=str(s).lower().replace('new_thyroid','newthyroid').replace('new-thyroid','newthyroid')
    s=re.sub(r'[^a-z0-9]','',s)
    for a,b in ALIAS: s=s.replace(a,b)
    return s
ALIAS=[('kddcup','kdd'),('rootkitimap','rootkit'),('krvskzeroone','krvsk01'),('krvskzero','krvsk0'),('krvskone','krvsk1'),('krvskthree','krvsk3'),
       ('fifteen','15'),('eleven','11'),('eight','8'),('draw','draw'),('segmemt','segment'),('habarman','haberman'),('abalone0918','abalone918')]

def parse_keel(p):
    attrs=0;rows=0;outs=None;labels={}
    names=[]
    with open(p,errors='ignore') as f:
        data=False
        for ln in f:
            l=ln.strip()
            if not l or l.startswith('%'):continue
            if data:
                rows+=1; lab=l.split(',')[-1].strip(); labels[lab]=labels.get(lab,0)+1
            elif l.lower().startswith('@attribute'): attrs+=1; names.append(l.split()[1])
            elif l.lower().startswith('@data'): data=True
    if attrs==0:
        import csv
        R=[r for r in csv.reader(open(p,errors='ignore')) if r]
        labels={}
        for r in R: labels[r[-1].strip()]=labels.get(r[-1].strip(),0)+1
        return dict(n=len(R),f=len(R[0])-1,classes=len(labels),minority=min(labels.values()),dist=sorted(labels.values()))
    return dict(n=rows,f=attrs-1,classes=len(labels),minority=min(labels.values()) if labels else None,dist=sorted(labels.values()))
C=[]
for p in glob.glob('src/kd/keel_ds/data/*/raw/*.dat'):
    nm=os.path.basename(p)[:-4]; C.append(dict(src='KEEL(keel_ds)',name=nm,path=p,**parse_keel(p)))
for d in glob.glob('src/idb/imbalanced_databases/data/*'):
    nm=os.path.basename(d); ps=[p for p in glob.glob(d+'/*.dat')]
    if ps: C.append(dict(src='KEEL(imbalanced_databases)',name=nm,path=ps[0],**parse_keel(ps[0])))
    else: C.append(dict(src='imbalanced_databases(other fmt)',name=nm,path=d,n=None,f=None,classes=None,minority=None,dist=None))
s=pd.read_csv('src/pmlb_summary.tsv',sep='\t'); s=s[s.task=='classification']
for _,r in s.iterrows(): C.append(dict(src='PMLB',name=r.dataset,path=None,n=int(r.n_instances),f=int(r.n_features),classes=int(r.n_classes),minority=None,dist=None))
c=pd.DataFrame(C); c['key']=c.name.map(key)
if __name__=="__main__": c.to_json('catalog.json',orient='records')
if __name__=="__main__": print(c.src.value_counts()); print(c.key.nunique())
