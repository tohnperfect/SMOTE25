import pandas as pd,re,itertools,glob,os,json
o=pd.read_csv('match.csv'); c=pd.read_json('catalog.json')
d=pd.read_csv('/mnt/user-data/uploads/SMOTE25/Data section/out/dataset_records.csv').set_index('record_id')
dist={r['name']:r['dist'] for _,r in c.iterrows() if isinstance(r['dist'],list)}
for p in glob.glob('src/pmlb/*.tsv.gz'):
    x=pd.read_csv(p,sep='\t'); dist[os.path.basename(p)[:-7]]=sorted(x.target.value_counts().tolist())
def n(v):
    m=re.search(r'\d[\d,]*',str(v)) if pd.notna(v) else None
    return int(m.group().replace(',','')) if m else None
def subsets(ds,t):
    if len(ds)>12: return None
    return sum(1 for k in range(1,len(ds)) for s in itertools.combinations(range(len(ds)),k) if sum(ds[i] for i in s)==t)
rows=[]
for _,r in o.iterrows():
    rec=d.loc[r.record_id]; pm=n(rec.n_minority); pc=n(rec.n_classes); st=r.status; cat=r.category
    ds=dist.get(r.file) if isinstance(r.file,str) else None
    if cat=='synthetic': v='U-synthetic'
    elif st=='no_file': v='U-no_public_file'
    elif st=='file_but_no_printed_size':
        # Toon 28 Oct: KEEL file with exact name counts as verifiable; modified entries are not the file itself
        if cat=='modified': v='U-no_printed_size'
        elif str(r.file_src).startswith('KEEL'): v='V-keel_name_only'
        else: v='V-name_only_other'   # Toon 28 Oct: pull non-KEEL files when obtainable; source recorded
    elif st in('size_mismatch','near_<=2pct','n_match_feat_diff'): v='U-size_mismatch'
    elif ds is None: v='U-no_class_info'
    elif len(ds)==2:
        if pm is None or pm==ds[0]: v='V-binary_file'
        else: v='U-minority_mismatch'
    else:  # multiclass file
        if (pc==len(ds)) and (pm is None or pm==ds[0]): v='V-multiclass_asis'
        elif pm is not None:
            k=subsets(ds,pm)
            v='V-binarized_rule_unique' if k==1 else ('V?-binarized_rule_ambiguous' if k and k>1 else 'U-task_not_reconstructible')
        else: v='U-task_not_reconstructible'
    rows.append(v)
o['verif']=rows
o['note_structure']=o.verif.map(lambda x:'paper reports only the dataset name; structure taken from the named file' if x in('V-name_only_other','V-keel_name_only') else '')
o.to_csv('verif.csv',index=False)
import sys
print(pd.crosstab(o.verif,o.category,margins=True).to_string())
V=o[o.verif.str.startswith('V-')]
print('\nentries V',len(V),'papers',V.paper.nunique(),'files',V.file.nunique())
print(V.groupby('verif').file.nunique())
# distinct tasks: file + minority size
V=V.assign(task=V.file+'|'+V.record_id.map(lambda i:str(n(d.loc[i,'n_minority']))))
print('binary file tasks',V[V.verif=='V-binary_file'].file.nunique())
