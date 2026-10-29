"""Build 'SMOTE Family at 25' (Method section/smote-family-overview.html): four
windows (definitions, roadmap, should we keep oversampling, reader takeaways),
with every number computed in the page from the Method Map records embedded here.
Usage: make_overview.py MAP OUT TEMPLATE"""
import json, re, sys

src = open(sys.argv[1], encoding='utf-8').read()
D = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', src, flags=re.S).group(1))
SF = sorted([p for p in D if p['smote_based']], key=lambda p: (p['year'], p['acronym'].lower()))
assert len(SF) == 37 and all(p.get('class_category') for p in SF)

NAME = {'DSRBF / SSRBF (Static-SMOTE)': 'SSRBF / DSRBF', 'SMOTE-Tomek / SMOTE-ENN': 'SMOTE-Tomek / ENN', 'SVDDWSMOTE': 'SVDD-WSMOTE'}
CODE = {'Binary only': 'B', 'Multiclass only': 'M', 'Binary + Multiclass': 'BM'}
# How Binary-only papers reached two classes (hand-coded from class_reduced, 28 Oct 2026; same sets as make_summary2.py)
SELF = {'P06', 'P08', 'P09', 'P12', 'P13', 'P15', 'P18', 'P22', 'P24', 'P28', 'P30', 'P31', 'P35', 'P61', 'P72'}
READY = {'P26', 'P39', 'P43', 'P51', 'P55', 'P57', 'P74', 'P75'}
PROVISIONAL = {'P74', 'P62'}
# Region- or distribution-based generators outside the family (Not counted, generate but not between two instances)
REGION = {'MDO', 'AMDO', 'RBO', 'MC-CCR', 'MC-RBO', 'CBHSID', 'GDO', 'SHSampler', 'MC-NCLWO', 'MLOS'}

rows = []
for p in SF:
    red = 'self' if p['uid'] in SELF else 'ready' if p['uid'] in READY else ('own' if p['class_category'] == 'Binary only' else None)
    rows.append({'id': p['uid'], 'n': NAME.get(p['acronym'], p['acronym']), 'y': p['year'], 'c': CODE[p['class_category']],
                 'rel': p['smote_rel'], 's': p['smote_via'], 'd': p['data_type'], 'mc': p['mc_strategy'] or '',
                 'red': red, 'pv': p['uid'] in PROVISIONAL, 'x': p['smote_explain']})
assert sum(1 for r in rows if r['red'] == 'own') == 1
region = [{'n': q['acronym'], 'y': q['year']} for q in D if q['acronym'] in REGION]
assert len(region) == 10
corpus = {'papers': len(D), 'core': sum(q['smote_rel'] == 'Core' for q in D), 'partial': sum(q['smote_rel'] == 'Partial' for q in D),
          'study': sum(q['smote_rel'] == 'Study' for q in D), 'notcounted': sum(q['smote_rel'] == 'Not counted' for q in D),
          'nolink': sum(not q['smote_rel'] for q in D)}
payload = json.dumps({'sf': rows, 'region': region, 'corpus': corpus}, ensure_ascii=False).replace('</', '<\\/')

out = open(sys.argv[3], encoding='utf-8').read()
assert out.count('{{DATA}}') == 1
open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(out.replace('{{DATA}}', payload))
print('written', corpus)
