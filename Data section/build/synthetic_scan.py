"""Scan every PDF of the corpus for (a) passages that describe author-generated (synthetic) data and
(b) sentences that say where data or code can be obtained (8 Nov 2026, Claude; Toon asked whether the synthetic
datasets are published, counted over all 76 papers).

This is a search aid, not a classification: it writes out/synthetic_scan.json with the matching sentences per paper
so the reader can open the PDF at the right place. The classification (published / cited source / code only /
on request / not found) is in build/synthetic_availability.py, where every evidence quote is asserted to occur in
the PDF text.

Run from Data section/ on the machine that holds paper/ (PDFs are not in git):  python3 build/synthetic_scan.py
"""
import json, re, subprocess, os, glob

PM = json.load(open('out/pdf_map.json'))
GEN = re.compile(r'(synthetic(ally)?[ -](generated )?(data|dataset|data ?set|problem|benchmark)s?|artificial(ly)?[ -](generated )?(data|dataset|data ?set|problem)s?|'
                 r'toy (data|dataset|example|problem)s?|simulated (data|dataset|data ?set)s?|we generate[ds]?|were generated|was generated|generated (according|from|by|using|with)|'
                 r'two-dimensional (data|dataset|example)|gaussian distribution|data generator|madelon)', re.I)
AVAIL = re.compile(r'(https?://\S+|github|available (at|from|online|upon|on request)|can be (found|downloaded|obtained)|download|'
                   r'supplementary|upon (reasonable )?request|on request|publicly available|repository of|web-?page|website)', re.I)

def text(path):
    t = subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True, text=True).stdout
    return re.sub(r'-\n\s*', '', t)

def sentences(t):
    t = re.sub(r'\s+', ' ', t)
    return re.split(r'(?<=[.;])\s+(?=[A-Z(\[])', t)

out = {}
for k, v in sorted(PM.items()):
    files = [v['main']] + list(v.get('supp') or [])
    gen, av = [], []
    for f in files:
        if not os.path.exists(f): continue
        for s in sentences(text(f)):
            if len(s) > 600: s = s[:600]
            if GEN.search(s): gen.append(s)
            if AVAIL.search(s): av.append(s)
    out[k] = dict(files=files, n_gen=len(gen), n_avail=len(av), gen=gen[:40], avail=av[:60])
json.dump(out, open('out/synthetic_scan.json', 'w'), indent=1, ensure_ascii=False)
print(len(out), 'papers scanned')
for k, v in out.items(): print(f"{k[:28]:28s} gen {v['n_gen']:3d}  avail {v['n_avail']:3d}")
