"""What happened to the 200 dataset names that had no public file on 8 Nov (first round)  (8 Nov 2026, Claude; Toon:
"the remaining ~200 come from public benchmarks; download what can be downloaded and leave the ones that are not published").

Reads  out/names_to_download_round1.csv   the 200 names (frozen copy of out/names_to_download.csv before the second round)
       out/names_download_check.csv       Toon's own check of the same 200 names (status A_author / A_repo / B_rebuild /
                                          C_identify / D_none, where, url) -- used as given, only to report it next to ours
       difficulty/verifiability_entries.csv   the status of every entry after the second round (verify_ext.py)
       out/dataset_records.csv            to map record_id -> normalized name
Writes out/names_download_result.csv (one row per name) and out/names_download_result.json (counts).

A name counts as "now verifiable" when at least one of its entries has a V- status after the second round. The other names
keep the reason of their entries, grouped as:
  file obtained, size or task does not match   a public or author file was found, but the printed size / minority / classes
                                               do not fit it (U-size_mismatch, U-minority_mismatch, U-task_not_reconstructible,
                                               U-name_ambiguous, V? ambiguous)
  modified, no printed size                    Toon 28 Oct rule (decision ก): a modified entry needs a printed size
  synthetic                                    author-generated (not measured, Toon 28 Oct)
  no file obtained                             still no file: Kaggle (sign-in needed), dead site (HDDT), private data,
                                               image/time-series/text corpora not loaded, or not identifiable from the name
The "no file obtained" names carry Toon's check status and source so the reason can be read per name.
"""
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
N = pd.read_csv('out/names_to_download_round1.csv')
C = pd.read_csv('out/names_download_check.csv', encoding='utf-8-sig')[['normalized_name', 'status', 'where', 'note']]
V = pd.read_csv('difficulty/verifiability_entries.csv')
R = pd.read_csv('out/dataset_records.csv', dtype=str).set_index('record_id')

GROUP = {'U-size_mismatch': 'file obtained, size or task does not match', 'U-minority_mismatch': 'file obtained, size or task does not match',
         'U-task_not_reconstructible': 'file obtained, size or task does not match', 'U-name_ambiguous': 'file obtained, size or task does not match',
         'V?-binarized_rule_ambiguous': 'file obtained, size or task does not match',
         'U-no_printed_size': 'modified, no printed size', 'U-synthetic': 'synthetic', 'U-no_public_file': 'no file obtained',
         'U-no_class_info': 'file obtained, size or task does not match'}
ORDER = ['now verifiable', 'file obtained, size or task does not match', 'modified, no printed size', 'synthetic', 'no file obtained']

rows = []
for r in N.itertuples():
    ids = [x.strip() for x in str(r.record_ids).split(';')]
    st = V.set_index('record_id').reindex(ids)
    ok = st[st.verif.astype(str).str.startswith('V-')]
    if len(ok):
        res, why = 'now verifiable', '; '.join(f'{i}:{v} ({s}:{f})' for i, v, s, f in zip(ok.index, ok.verif, ok.file_src, ok.file))
    else:
        g = [GROUP.get(v, 'no file obtained') for v in st.verif.astype(str)]
        res = min(g, key=ORDER.index)
        why = '; '.join(f'{i}:{v}' + (f' ({b})' if isinstance(b, str) and b else '') for i, v, b in zip(st.index, st.verif, st.basis))
    rows.append(dict(normalized_name=r.normalized_name, name_type=r.name_type, papers=r.papers, entries=len(ids),
                     entries_verifiable=len(ok), result=res, detail=why[:400]))
O = pd.DataFrame(rows).merge(C.rename(columns={'status': 'toon_check_status', 'where': 'toon_check_where', 'note': 'toon_check_note'}),
                             on='normalized_name', how='left')
O['result'] = pd.Categorical(O.result, ORDER, ordered=True)
O = O.sort_values(['result', 'normalized_name'])
O.to_csv('out/names_download_result.csv', index=False)
J = dict(names=len(O), entries=int(O.entries.sum()),
         by_result={k: dict(names=int((O.result == k).sum()), entries=int(O[O.result == k].entries.sum()),
                            entries_verifiable=int(O[O.result == k].entries_verifiable.sum())) for k in ORDER},
         no_file_by_toon_check=O[O.result == 'no file obtained'].toon_check_status.fillna('-').value_counts().to_dict(),
         no_file_by_where=O[O.result == 'no file obtained'].toon_check_where.fillna('-').str.split(r' \(|/| \+').str[0].str.strip().value_counts().to_dict())
json.dump(J, open('out/names_download_result.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(J, indent=1, ensure_ascii=False))
