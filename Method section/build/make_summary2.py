"""Build 'SMOTE Family by Class Setting' (v2: PDF-checked class categories and
how each method builds on SMOTE) from the Method Map data.
Usage: make_summary2.py MAP OUT TEMPLATE"""
import json, re, sys, html as H
from collections import Counter

src = open(sys.argv[1], encoding='utf-8').read()
m = re.search(r'<script type="application/json" id="data">(.*?)</script>', src, flags=re.S)
D = json.loads(m.group(1))
SF = sorted([p for p in D if p['smote_based']], key=lambda p: (p['year'], p['acronym'].lower()))
assert len(SF) == 37 and all(p.get('class_category') for p in SF)

CATS = [('Binary only', 'B', 'Every experiment that generates data is two-class. A multiclass dataset reduced to two classes counts here, and so does a multiclass extension that is only described.'),
        ('Multiclass only', 'M', 'Generates data with three or more classes kept, and is never run on two-class data.'),
        ('Binary + Multiclass', 'BM', 'The same generator is run on two-class data and on data with three or more classes kept, without reducing it first.')]
STEPS = ['Seed selection', 'Sample allocation', 'Neighbour choice', 'Placement rule', 'Post-filtering', 'Inside a pipeline']
SHORT = ['Seed', 'Alloc.', 'Partner', 'Place', 'Filter', 'Pipeline']
NAME = {'DSRBF / SSRBF (Static-SMOTE)': 'SSRBF / DSRBF', 'SMOTE-Tomek / SMOTE-ENN': 'SMOTE-Tomek / ENN', 'SVDDWSMOTE': 'SVDD-WSMOTE'}
PROVISIONAL = {'P74', 'P62'}
e = lambda s: H.escape(str(s), quote=True)
nm = lambda p: NAME.get(p['acronym'], p['acronym'])
code = {c[0]: c[1] for c in CATS}

def chip(p):
    return '<span class="m%s">%s<i>%s</i></span>' % (' prov' if p['uid'] in PROVISIONAL else '', e(nm(p)), str(p['year'])[2:])

# board
board = []
for name, c, d in CATS:
    ps = [p for p in SF if p['class_category'] == name]
    board.append('<div class="col c-%s"><div class="ch"><b>%s</b><span class="big">%d</span></div><p>%s</p><div class="ms">%s</div></div>'
                 % (c, e(name), len(ps), e(d), ''.join(chip(p) for p in ps)))

# numbers for findings
n = Counter(p['class_category'] for p in SF)
per = lambda y: 0 if y < 2010 else 1 if y < 2018 else 2
tot = Counter(per(p['year']) for p in SF)
multi = Counter(per(p['year']) for p in SF if p['class_category'] != 'Binary only')
# Hand-coded from class_reduced (28 Oct 2026): authors reduce multiclass sources themselves
# vs use ready-made (mostly KEEL) two-class splits without describing a reduction.
SELF = {'P06', 'P08', 'P09', 'P12', 'P13', 'P15', 'P18', 'P22', 'P24', 'P28', 'P30', 'P31', 'P35', 'P61', 'P72'}
READY = {'P26', 'P39', 'P43', 'P51', 'P55', 'P57', 'P74', 'P75'}
bo = {p['uid'] for p in SF if p['class_category'] == 'Binary only'}
assert SELF | READY | {'P10'} == bo and not SELF & READY, bo ^ (SELF | READY | {'P10'})
b_reduced = '%d of them evaluate on multiclass sources reduced to two classes: %d reduce the classes themselves (one class against the rest, merged classes, or two classes kept and the rest dropped) and %d use ready-made two-class splits such as KEEL\'s <i>yeast-2_vs_4</i> without describing the reduction. The remaining one, Cluster-SMOTE, collapses the attack types of its own network data into intrusive vs not' % (len(SELF) + len(READY), len(SELF), len(READY))
steps = Counter(s for p in SF for s in p['smote_via'])
changed = sum(1 for p in SF if sorted(p['smote_via']) != sorted(p.get('smote_via_v1', [])))
nb = n['Binary only']
vals = {
    '{{NB}}': nb, '{{NM}}': n['Multiclass only'], '{{NBM}}': n['Binary + Multiclass'],
    '{{P0}}': '%d of %d' % (multi[0], tot[0]), '{{P1}}': '%d of %d' % (multi[1], tot[1]), '{{P2}}': '%d of %d' % (multi[2], tot[2]),
    '{{BRED}}': b_reduced, '{{CHANGED}}': changed,
    '{{STEPS}}': ', '.join('%s %d' % (s.lower(), steps[s]) for s in STEPS),
}
assert n['Binary only'] + n['Multiclass only'] + n['Binary + Multiclass'] == 37

# table
rows = []
for p in SF:
    c = code[p['class_category']]
    dots = ''.join('<td class="d">%s</td>' % ('●' if s in p['smote_via'] else '') for s in STEPS)
    rows.append('<tr><td class="nm">%s<span class="yr">%d</span></td><td><span class="pill p-%s">%s</span>%s</td>%s<td class="ex">%s</td></tr>'
                % (e(nm(p)), p['year'], c, e(p['class_category']), ' <span class="prov-t">provisional</span>' if p['uid'] in PROVISIONAL else '',
                   dots, e(p['smote_explain'])))
head = ''.join('<th scope="col" class="d" title="%s">%s</th>' % (e(s), e(sh)) for s, sh in zip(STEPS, SHORT))
tot_row = '<tr class="tot"><td>Papers changing each step</td><td></td>%s<td></td></tr>' % ''.join('<td class="d">%d</td>' % steps[s] for s in STEPS)

# Papers on other data types: class category per data type, from the 28 Oct PDF check
# (Method section/pdf-check/*.json). GAMO's tabular runs are in its supplement.
OTHER = {
    'P22': [('Time series', 'Binary only', '48 two-class tasks from 7 UCR datasets, each one class against the rest; Adiac (37 classes), FaceAll (14), 50words (50) and SLeaf (15) are reduced this way (Sec. 4.2, pp.7-8).')],
    'P40': [('Image', 'Multiclass only', 'MNIST, Fashion-MNIST, CIFAR10 and SVHN with 10 classes, CelebA and LSUN with 5, SUN397 with 50, all classes kept (Secs. 4.1-4.4, Tables 1-4).'),
            ('Tabular', 'Binary + Multiclass', 'Supplement only: Abalone19, IJCNN1 and Magic (two classes) and Chess (18 classes) and Cover Type (7 classes) (Supp. Sec. 4, Tables 7-8).')],
    'P57': [('Tabular', 'Binary only', '19 two-class datasets, 18 from KEEL plus CM1 (Table 2, Sec. 4.1, p.11).'),
            ('Image', 'Binary only', 'UTKFace with male faces as minority against female faces, and CIFAR-10 airplane against the other 9 classes; generated images are shown, no classification scores are reported (Sec. 6, p.14).')],
}
BYU = {p['uid']: p for p in SF}
other_rows = []
for uid in sorted(OTHER, key=lambda u: BYU[u]['year']):
    p = BYU[uid]
    first = True
    for dt, cat, ev in OTHER[uid]:
        other_rows.append('<tr>%s<td>%s</td><td><span class="pill p-%s">%s</span></td><td class="ex">%s</td>%s</tr>' % (
            '<td class="nm" rowspan="%d">%s<span class="yr">%d</span></td>' % (len(OTHER[uid]), e(nm(p)), p['year']) if first else '',
            e(dt), code[cat], e(cat), e(ev),
            '<td rowspan="%d"><span class="pill p-%s">%s</span></td>' % (len(OTHER[uid]), code[p['class_category']], e(p['class_category'])) if first else ''))
        first = False
outside = [q for q in D if not q['smote_based'] and any(d in ('Image', 'Text', 'Time series') for d in q['data_type'])]
outside_txt = ', '.join('%s (%d, %s)' % (e(q['acronym'].split(' (')[0]), q['year'], e(', '.join(d.lower() for d in q['data_type'] if d != 'Tabular'))) for q in sorted(outside, key=lambda q: q['year']))

# Timeline data
TL = [{'id': p['uid'], 'n': nm(p), 'y': p['year'], 'c': code[p['class_category']], 'cat': p['class_category'],
       'pv': p['uid'] in PROVISIONAL, 'd': list(p['data_type']),
       's': p['smote_via'], 'l': p['smote_rel'], 'x': p['smote_explain'], 'e': p['class_evidence_pdf']} for p in SF]
tl_json = json.dumps(TL, ensure_ascii=False).replace('</', '<\\/')

out = open(sys.argv[3], encoding='utf-8').read()
reps = {'{{BOARD}}': ''.join(board), '{{HEAD}}': head, '{{ROWS}}': ''.join(rows) + tot_row,
        '{{OTHERROWS}}': ''.join(other_rows), '{{OUTSIDE}}': outside_txt, '{{TLDATA}}': tl_json,
        '{{NOTHER}}': str(len(OTHER))}
reps.update({k: str(v) for k, v in vals.items()})
for k, v in reps.items():
    assert out.count(k) >= 1, k
    out = out.replace(k, v)
assert '{{' not in out
open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(out)
print('written', n, dict(multi), dict(tot), 'bred', b_reduced, 'changed', changed, steps)
