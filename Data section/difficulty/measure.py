"""Measure data-difficulty characteristics for verifiable tasks (Toon decisions 28 Oct 2026).
Revised 28 Oct 2026 (Toon): rare follows Napierala & Stefanowski (2016) sec. 5.2.1 incl. the condition on the
same-class neighbour; rare_simple_1of5 keeps the previous rule (any 1:4) for comparison.
Revised 28 Oct 2026 (Toon): neighbourhoods use HVDM, as Napierala & Stefanowski (2016) do, defined by
Wilson & Martinez (1997, JAIR 6:1-34): HVDM(x,y) = sqrt(sum_a d_a^2), numeric d_a = |x_a-y_a| / (4 sd_a),
nominal d_a = normalized_vdm N2 = sqrt(sum_c (P(c|x_a) - P(c|y_a))^2) with c = the task's two classes.
Implemented exactly as Euclidean distance on an embedding: numeric x/(4 sd), nominal value -> (P(min|v), P(maj|v)).
Nominal = KEEL header '{...}' or non-numeric values; PMLB nominals are label-encoded and are treated as numeric.
Rows with missing values are dropped (so HVDM's d_a = 1 for unknowns is never used). sd uses ddof=1.
T2 / T4 stay on the min-max + one-hot encoding (dimension measures, not neighbourhoods).
Factors: noise (overlap merged in), small disjuncts, small sample / rarity, plus IR.
Defaults (Claude, not yet reviewed): k=5, Euclidean on min-max scaled numeric + one-hot nominal,
rows with missing values dropped, duplicates kept; multiclass files -> one-vs-rest for every class."""
import pandas as pd,numpy as np,glob,os,re,itertools,csv
from sklearn.neighbors import NearestNeighbors
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from catalog import key
K=5
o=pd.read_csv('verifiability_entries.csv'); o=o[o.verif.str.startswith('V-')]
rec=pd.read_csv(os.environ.get('DATASET_RECORDS','../out/dataset_records.csv')).set_index('record_id')
idb={key(os.path.basename(d)):glob.glob(d+'/*.dat') for d in glob.glob('src/idb/imbalanced_databases/data/*')}
def load(fname,src):
    k=key(fname)
    if src=='PMLB':
        d=pd.read_csv(f'src/pmlb/{fname}.tsv.gz',sep='\t'); y=d.pop('target').astype(str); return d,y,'pmlb(label-encoded)'
    if src.startswith('imbalanced_databases(other'):
        base=f'src/idb/imbalanced_databases/data/{fname}/'
        if fname=='glass':
            d=pd.read_csv(base+'glass.data.txt',header=None,dtype=str); d=d.drop(columns=[0]); y=d.pop(10); return d,y,'UCI file via imbalanced_databases'
        if fname=='hepatitis':
            d=pd.read_csv(base+'hepatitis.data.txt',header=None,dtype=str); y=d.pop(0); return d,y,'UCI file via imbalanced_databases'
        raise ValueError(fname)
    if idb.get(k):
        p=idb[k][0]; names=[];nom=set();rows=[];data=False
        for ln in open(p,errors='ignore'):
            l=ln.strip()
            if not l or l.startswith('%'):continue
            if data: rows.append([x.strip() for x in l.split(',')])
            elif l.lower().startswith('@attribute'):
                nm=l.split()[1]; names.append(nm)
                if '{' in l: nom.add(nm)
            elif l.lower().startswith('@data'): data=True
        d=pd.DataFrame(rows,columns=names); y=d.pop(names[-1]); nom.discard(names[-1])
        return d.assign(**{c:d[c].astype('category') for c in nom}),y,'keel(header)'
    p=[q for q in glob.glob('src/kd/keel_ds/data/*/raw/*.dat') if key(os.path.basename(q)[:-4])==k][0]
    d=pd.read_csv(p,header=None,dtype=str,skipinitialspace=True); y=d.pop(d.columns[-1]); d.columns=[f'a{i}' for i in range(d.shape[1])]
    return d,y,'keel(raw,no header)'
def encode(d):
    d=d.replace('?',np.nan).replace('<null>',np.nan)
    keep=d.notna().all(axis=1); d=d[keep]; cols=[]
    for c in d.columns:
        if str(d[c].dtype)=='category': cols.append(pd.get_dummies(d[c].astype(str),prefix=c).astype(float)); continue
        v=pd.to_numeric(d[c],errors='coerce')
        if v.isna().any(): cols.append(pd.get_dummies(d[c].astype(str),prefix=c).astype(float))
        else:
            r=v.max()-v.min(); cols.append(((v-v.min())/(r if r else 1)).to_frame())
    return pd.concat(cols,axis=1).values,keep
def typed(d):
    """Drop rows with missing values; return the cleaned frame, the kept-row mask and the nominal columns."""
    d=d.replace('?',np.nan).replace('<null>',np.nan)
    keep=d.notna().all(axis=1); d=d[keep]; nominal=[]
    for c in d.columns:
        if str(d[c].dtype)=='category' or pd.to_numeric(d[c],errors='coerce').isna().any(): nominal.append(c)
    return d,keep,nominal
def hvdm_embed(d,nominal,ymin):
    cols=[]
    for c in d.columns:
        if c in nominal:
            v=d[c].astype(str).values; t=pd.crosstab(v,ymin); t=t.div(t.sum(axis=1),axis=0)
            pmin=t[True] if True in t.columns else 0*t.iloc[:,0]; pmaj=t[False] if False in t.columns else 0*t.iloc[:,0]
            cols+= [pd.Series(v).map(pmin).values, pd.Series(v).map(pmaj).values]
        else:
            x=pd.to_numeric(d[c]).astype(float).values; sd=x.std(ddof=1) if len(x)>1 else 0
            cols.append(x/(4*sd) if sd>0 else np.zeros(len(x)))
    return np.column_stack(cols)
def point_types(XH,ymin):
    """Napierala & Stefanowski (2016) sec. 5.2.1, k=5, on the HVDM embedding.
    S 5:0/4:1, B 3:2/2:3, O 0:5; a 1:4 example is R only if its single same-class neighbour has 0:5, or 1:4
    pointing back to the analysed example; otherwise B. Returns kNN index matrix, minority indices,
    same-class neighbour counts and one type letter per minority example."""
    n=len(ymin)
    nn=NearestNeighbors(n_neighbors=K+1).fit(XH); _,I=nn.kneighbors(XH); I=I[:,1:]
    mi=np.where(ymin)[0]; same=ymin[I[mi]].sum(1)
    same_all=np.zeros(n,dtype=int); same_all[mi]=same
    ptype=np.where(same>=4,'S',np.where(same==0,'O','B')).astype(object)
    for a,g in enumerate(mi):
        if same[a]!=1: continue
        j=[h for h in I[g] if ymin[h]][0]
        sj=same_all[j]
        if sj==0 or (sj==1 and [h for h in I[j] if ymin[h]][0]==g): ptype[a]='R'
    return I,mi,same,ptype
def measures(X,ymin,XH):
    """X: min-max + one-hot (T2/T4 only); XH: HVDM embedding (all neighbourhood measures)."""
    n=len(ymin); nmin=int(ymin.sum())
    I,mi,same,ptype=point_types(XH,ymin)
    is_r=ptype=='R'
    rare_simple=(same==1).mean()
    safe=(ptype=='S').mean(); rare=is_r.mean(); outl=(ptype=='O').mean(); border=(ptype=='B').mean()
    kdn=1-same.mean()/K
    # minority sub-concepts: components of graph linking minority points to minority kNN
    pos={g:i for i,g in enumerate(mi)}; r=[];c=[]
    for a,g in enumerate(mi):
        for h in I[g]:
            if ymin[h]: r.append(a); c.append(pos[h])
    G=csr_matrix((np.ones(len(r)),(r,c)),shape=(nmin,nmin))
    ncomp,lab=connected_components(G,directed=False); sizes=np.bincount(lab)
    # density / dimensionality (Toon asked 28 Oct)
    from sklearn.decomposition import PCA
    T2=n/X.shape[1]
    try: T4=int(np.searchsorted(np.cumsum(PCA().fit(X).explained_variance_ratio_),0.95)+1)/X.shape[1]
    except Exception: T4=np.nan
    def kd(Z):
        if len(Z)<K+1: return np.nan
        dd,_=NearestNeighbors(n_neighbors=K+1).fit(Z).kneighbors(Z); return dd[:,1:].mean()
    dmin,dmaj=kd(XH[ymin]),kd(XH[~ymin])
    dens=dict(T2_points_per_dim=round(T2,2),T4_pca95_share=round(T4,3),min_knn_dist=round(dmin,4) if dmin==dmin else None,
              maj_knn_dist=round(dmaj,4),min_sparsity_ratio=round(dmin/dmaj,3) if (dmin==dmin and dmaj) else None)
    return dict(**dens,N=n,n_min=nmin,IR=round((n-nmin)/nmin,3),safe=round(safe,3),borderline=round(border,3),rare=round(rare,3),outlier=round(outl,3),rare_simple_1of5=round(rare_simple,3),
        kDN_min=round(kdn,3),noise_index=round(border+outl,3),n_subconcepts=int(ncomp),subconcepts_ge2=int((sizes>=2).sum()),
        largest_subconcept_share=round(sizes.max()/nmin,3),singletons=int((sizes==1).sum()))
def subset(ds_labels,counts,t):
    sols=[s for k in range(1,len(counts)) for s in itertools.combinations(range(len(counts)),k) if sum(counts[i] for i in s)==t]
    return [ds_labels[i] for i in sols[0]] if len(sols)==1 else None
def iter_tasks():
    """Yield every verifiable task: (file, source, loader, X, typed frame, nominal cols, task_type, label, ymin, who, nfeat, keep).
    Shared by main() and projection.py so both see the same rows and minority definition."""
    tasks={}
    for _,r in o.iterrows():
        tasks.setdefault((r.file,r.file_src),[]).append((r.verif,r.record_id,r.paper))
    for (f,src),lst in tasks.items():
        d,y,how=load(f,src); X,keep=encode(d); y=y[keep].astype(str).values
        dt,keep2,nominal=typed(d); assert (keep2==keep).all()
        labs,cnt=np.unique(y,return_counts=True); nfeat=d.shape[1]
        todo={}
        for kind,rid,paper in lst:
            if len(labs)==2: todo.setdefault(('binary',labs[np.argmin(cnt)]),[]).append((rid,paper))
            elif kind=='V-binarized_rule_unique':
                m=re.search(r'\d+',str(rec.loc[rid,'n_minority'])); s_=subset(list(labs),list(cnt),int(m.group()))
                if s_: todo.setdefault(('binarized','+'.join(s_)),[]).append((rid,paper))
                else: LOG.append((f,rid,'subset not unique after missing-row drop'))
            else:
                for l in labs: todo.setdefault(('ovr',l),[]).append((rid,paper))
        for (t,lab),who in todo.items():
            ymin=np.isin(y,lab.split('+')) if t=='binarized' else (y==lab)
            if ymin.sum()<2: LOG.append((f,lab,'minority <2 rows')); continue
            yield f,src,how,X,dt,nominal,t,lab,ymin.astype(bool),who,nfeat,keep
LOG=[]
def main():
    out=[]
    for f,src,how,X,dt,nominal,t,lab,ymin,who,nfeat,keep in iter_tasks():
        m=measures(X,ymin,hvdm_embed(dt,nominal,ymin))
        out.append(dict(file=f,source=src,loader=how,task_type=t,minority_label=lab,n_features_raw=nfeat,n_features_encoded=X.shape[1],n_nominal=len(nominal),distance='HVDM',
            rows_dropped_missing=int((~keep).sum()),min_share_ge_half=m['n_min']/m['N']>=0.5,
            n_min_per_feature=round(m['n_min']/nfeat,2),entries=len(who),papers='; '.join(sorted({p for _,p in who})),**m))
    R=pd.DataFrame(out); R.to_csv('difficulty_measures.csv',index=False)
    pd.DataFrame(LOG,columns=['file','item','note']).to_csv('measure_log.csv',index=False)
    print(len(R),'tasks'); print(R.task_type.value_counts()); print(len(LOG),'log')
if __name__=="__main__": main()
