"""Provisional grouping (Claude, 28 Oct 2026; Toon not yet reviewed).
Toon 28 Oct: overlap is merged into noise. Types: safe if safe share >= SAFE_T; otherwise the larger of
noise (= borderline + outlier) and rare (small disjuncts). Second axis: small sample if minority examples per
original feature < SMALL_T. Tasks whose 'minority' is >= 50% are excluded.
version_note: file came from a non-KEEL mirror and some entries using it were matched by name only."""
import pandas as pd,sys
SAFE_T,SMALL_T=0.5,5
R=pd.read_csv('difficulty_measures.csv')
o=pd.read_csv('verif.csv')
RISK={'ecoli':'PMLB 327; corpus mostly 336','yeast':'PMLB 1479; corpus mostly 1484','dermatology':'PMLB 366; corpus mostly 358 (KEEL)',
      'shuttle':'PMLB 58000; corpus prints 2175/14500/43500/57999','adult':'PMLB 48842; corpus also 32562','spect':'PMLB 267; corpus 268',
      'balance_scale':'no size printed anywhere in corpus'}
sized=set(o[o.verif.isin(['V-binary_file','V-multiclass_asis','V-binarized_rule_unique'])].file)
NOTE='paper reports only the dataset name, not its size or class proportions; structure taken from the named file'
nameonly=o[o.verif=='V-name_only_other'].groupby('file').paper.apply(lambda s:'; '.join(sorted(set(s))))
def vnote(f):  # Toon 28 Oct: keep all 31 tasks; use the named file's structure and note it
    if f not in RISK: return ''
    return f'{NOTE} ({nameonly.get(f,"")}); file: {RISK[f]}'
R['version_note']=R.file.map(vnote)
def typ(r,st):
    if r.safe>=st: return 'safe'
    return 'noise' if r.noise_index>=r.rare else 'rare'
def grp(st,sm):
    t=R.apply(lambda r:typ(r,st),axis=1); s=R.n_min_per_feature<sm
    g=t+s.map({True:' + small sample',False:''}); g[R.min_share_ge_half]='excluded'; return t,s,g
R['type'],R['small_sample'],R['group']=grp(SAFE_T,SMALL_T)
R.to_csv('difficulty_groups.csv',index=False)
G=R[R.group!='excluded']; B=G[G.task_type!='ovr']
print(len(R),'tasks;',len(G),'grouped')
print(pd.crosstab(G.type,G.small_sample,margins=True)); print('binary+binarized'); print(pd.crosstab(B.type,B.small_sample,margins=True))
# sensitivity
rows=[]
base=R.group
for st in [0.4,0.5,0.6]:
    for sm in [3,5,10]:
        t,s,g=grp(st,sm); keep=g!='excluded'; bk=keep&(R.task_type!='ovr')
        rows.append(dict(safe_t=st,small_t=sm,
            changed_all=round((g[keep]!=base[keep]).mean()*100,1),changed_type_all=round((t[keep]!=R.type[keep]).mean()*100,1),
            changed_binary=round((g[bk]!=base[bk]).mean()*100,1),
            **{f'all_{k}':int((t[keep]==k).sum()) for k in ['safe','noise','rare']},
            all_small=int(s[keep].sum()),
            **{f'bin_{k}':int((t[bk]==k).sum()) for k in ['safe','noise','rare']},bin_small=int(s[bk].sum())))
S=pd.DataFrame(rows); S.to_csv('group_sensitivity.csv',index=False); print(S.to_string())
print(R[R.version_note!=''].groupby('version_note').size())
