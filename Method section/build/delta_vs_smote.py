"""Difference from SMOTE for each SMOTE-family paper, and the three selection criteria.

Source: Data section/out/verified_outcomes.csv (per-dataset scores printed in each
paper's own results table, checked against the PDFs on 18 Oct 2026; one metric per
paper by the Data section rule: G-mean, else AUC, else F-measure, else accuracy).
Delta = proposed - SMOTE on a 0-1 scale (percentages divided by 100). Plain SMOTE is
used where the paper compares with it; otherwise SMOTE inside a multiclass or
ensemble wrapper (marked). Writes Method section/search/delta_vs_smote.json.
Usage, from the repo root: python "Method section/build/delta_vs_smote.py"
"""
import csv, json, re, statistics as st, os
from collections import defaultdict

ROOT = os.getcwd()
rows = list(csv.DictReader(open(os.path.join(ROOT, 'Data section', 'out', 'verified_outcomes.csv'), encoding='utf-8-sig')))
mm = open(os.path.join(ROOT, 'SMOTE25_Method_Map_1.html'), encoding='utf-8').read()
D = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', mm, flags=re.S).group(1))
SF = [p for p in D if p['smote_based']]

# outcome-file paper name -> Method Map acronym
NAMES = {'DSRBF / Static-SMOTE': 'DSRBF / SSRBF (Static-SMOTE)', 'OREM-M': 'OREM / OREM-M',
         'SMOTE-ENN / SMOTE-Tomek': 'SMOTE-Tomek / SMOTE-ENN', 'RBBoost / Random Balance': 'RBBoost',
         'SVDD-WSMOTE': 'SVDDWSMOTE'}
# no per-dataset pair in the paper (Data section, Sec. "Can the reported results be checked?")
NO_PAIR = {'Borderline-SMOTE': 'plots only', 'Safe-Level-SMOTE': 'plots only', 'Cluster-SMOTE': 'plots only',
           'k-means SMOTE': 'plots only', 'GLOS': 'plots only', 'G-SMOTE': 'averages only', 'CISO': 'averages only',
           'QC-SMOTE': 'averages only', 'KNNOR': 'mean only'}
# methods that remove or move original training examples (criterion 3), from the PDF-check accounts
REMOVES = {'SMOTE-Tomek / SMOTE-ENN': 'cleans both classes', 'LS': 'undersamples the majority', 'INOS': 'removes noise links',
           'RBBoost': 'undersamples', 'SCUT': 'undersamples large classes', 'SMOTE-IPF': 'filters both classes',
           'A-SUWO': 'removes noisy points of both classes', 'HDE': 'undersamples the majority',
           'SVDDWSMOTE': 'removes majority and noisy minority points', 'GLOS': 'removes sparse majority points',
           'NROMM': 'removes borderline majority points', 'MC-MBRC': 'moves overlapping majority points',
           'GDHS': 'removes majority points', 'Loyalty-SMOTE': 'removes noise of both classes'}

def norm(v):
    v = float(v)
    if v > 100:
        return None          # misprint in the source table (e.g. 9100); left out
    return v / 100 if v > 1.5 else v

agg = defaultdict(lambda: {'plain': [], 'wrap': [], 'metric': None, 'skipped': 0})
for r in rows:
    name = NAMES.get(r['paper'], r['paper'])
    try:
        a, b = norm(r['proposed']), norm(r['smote'])
    except ValueError:
        continue
    if a is None or b is None:
        agg[name]['skipped'] += 1
        continue
    agg[name]['plain' if r['smote_kind'] == 'plain SMOTE' else 'wrap'].append(a - b)
    agg[name]['metric'] = agg[name]['metric'] or r['metric']

out = []
for p in sorted(SF, key=lambda q: (q['year'], q['acronym'].lower())):
    a = p['acronym']
    g = agg.get(a)
    rec = {'uid': p['uid'], 'acronym': a, 'year': p['year'], 'category': p['class_category'], 'rel': p['smote_rel'],
           'steps': p['smote_via'], 'n_steps': len(p['smote_via'])}
    if a == 'SMOTE':
        rec.update(delta=None, note='reference')
    elif a == 'KNNOR':
        rec.update(delta=0.0125, wins=None, n=None, kind='mean of 19 datasets', note='mean only')
    elif g and (g['plain'] or g['wrap']):
        d, kind = (g['plain'], 'plain') if g['plain'] else (g['wrap'], 'wrapper')
        rec.update(delta=round(st.median(d), 4), wins=sum(x > 0 for x in d), losses=sum(x < 0 for x in d), n=len(d),
                   kind=kind, metric=g['metric'], skipped=g['skipped'])
    else:
        rec.update(delta=None, note=NO_PAIR.get(a, 'no comparison with SMOTE'))
    # criteria
    rec['c1_not_worse'] = None if rec.get('delta') is None else rec['delta'] >= 0
    rec['c2_simple'] = (rec['n_steps'] <= 2 and 'Inside a pipeline' not in p['smote_via'] and p['smote_rel'] == 'Core'
                        and a not in ('GAMO',))
    rec['c3_keeps_data'] = a not in REMOVES
    rec['removes'] = REMOVES.get(a, '')
    out.append(rec)

json.dump(out, open(os.path.join(ROOT, 'Method section', 'search', 'delta_vs_smote.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for r in out:
    dd = '   ref ' if r['acronym'] == 'SMOTE' else (f"{r['delta']:+.3f}" if r.get('delta') is not None else ' n/a  ')
    wl = f"{r.get('wins')}/{r.get('n')}" if r.get('n') else (r.get('note') or '')
    print(f"{r['acronym']:28} {r['category']:20} {dd} {wl:16} {r.get('kind',''):8} simple={r['c2_simple']!s:5} keeps={r['c3_keeps_data']!s:5} steps={r['n_steps']}")
