"""Extended mirror catalog (8 Nov 2026, Claude; Toon asked to pull every dataset that was not yet measured).

The KEEL / UCI / OpenML web sites are refused by the proxy from both the cloud and Toon's machine, so the files
come from public GitHub mirrors (fetched by fetch_mirrors_ext.sh into src/, not stored in git):

  KEEL-std(F)   Fuminides/keel_datasets          KEEL standard classification, .dat with KEEL header
  KEEL-std(C)   15399240803/keel_csv             KEEL standard classification, CSV (second, independent copy; used
                                                 as a cross-check of N / classes for KEEL-std(F), never measured)
  PMLB          EpistasisLab/pmlb (all 179 classification sets; nominals label-encoded)
  UCI++         lpfgarcia/ucipp                  UCI datasets in ARFF (Garcia et al., Zenodo 10.5281/zenodo.13748)
  Weka-UCI      renatopp/arff-datasets/classification   the UCI ARFF files distributed with Weka
  PROMISE-ck    klainfo/DefectData terapromise/ck      tera-PROMISE CK-metric defect sets (label = bug > 0)
  NASA-MDP      klainfo/DefectData terapromise/mccabe  NASA MDP McCabe/Halstead sets
  jbrownlee-UCI jbrownlee/Datasets               selected UCI CSVs (mammography, oil-spill, ...; no header)
  + (8 Nov 2026, second round) UCI-official, LibSVM and author repositories: see official_sources.py

parse(src, path) returns (features as a DataFrame of strings/categories, labels as str Series, loader note).
Nothing here decides whether a file is the one a paper used: that is verify_ext.py (printed size must match).
"""
import os, re, csv, glob, gzip, io
import pandas as pd, numpy as np
from catalog import key
import official_sources
OFFICIAL_SRC = {'UCI-official', 'LibSVM', 'author-HDE', 'author-DGOT', 'author-SOS', 'author-MBS', 'author-kmeans', 'Kaggle'}
OFFICIAL_BY_PATH = {s[2]: s for s in official_sources.SPEC}   # key = path under src/

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

def _keel_header(path):
    names, nom, rows, data = [], set(), [], False
    for ln in open(path, errors='ignore'):
        l = ln.strip()
        if not l or l.startswith('%'): continue
        if data:
            rows.append([x.strip() for x in next(csv.reader([l], skipinitialspace=True))])
        elif l.lower().startswith('@attribute'):
            m = re.match(r"@attribute\s+('([^']*)'|\"([^\"]*)\"|(\S+))\s*(.*)", l, re.I)
            nm = m.group(2) or m.group(3) or m.group(4); rest = m.group(5)
            names.append(nm)
            if rest.strip().startswith('{'): nom.add(nm)
        elif l.lower().startswith('@data'): data = True
    return names, nom, rows

CLASS_NAMES = ('class', 'classe', 'target', 'defects', 'defective', 'label', 'problems')

def _arff(path, class_attr=None):
    names, nom, rows = _keel_header(path)
    rows = [r for r in rows if len(r) == len(names)]
    d = pd.DataFrame(rows, columns=names)
    named = [n for n in names if n.strip().lower() in CLASS_NAMES]
    cls = class_attr if class_attr in names else (named[0] if named else names[-1])
    y = d.pop(cls).astype(str).str.strip().str.strip("'\""); nom.discard(cls)
    d = d.apply(lambda s: s.str.strip().str.strip("'\""))
    return d.assign(**{c: d[c].astype('category') for c in nom if c in d}), y

def parse(src, path):
    if src == 'KEEL-std(F)':
        d, y = _arff(path); return d, y, 'keel(header) GitHub mirror'
    if src == 'KEEL-std(C)':
        d = pd.read_csv(path, dtype=str); y = d.pop(d.columns[-1]).str.strip(); return d, y, 'keel csv mirror'
    if src == 'PMLB':
        d = pd.read_csv(path, sep='\t'); y = d.pop('target').astype(str); return d.astype(str), y, 'pmlb(label-encoded)'
    if src in ('UCI++', 'Weka-UCI', 'NASA-MDP'):
        d, y = _arff(path); return d, y, f'arff {src}'
    if src == 'jbrownlee-UCI':
        d = pd.read_csv(path, header=None, dtype=str, skipinitialspace=True)
        y = d.pop(d.columns[-1]).str.strip().str.strip("'\""); d.columns = [f'a{i}' for i in range(d.shape[1])]
        return d, y, 'jbrownlee csv (no header, last column = class)'
    if src == 'PROMISE-ck':
        d = pd.read_csv(path, dtype=str)
        y = (pd.to_numeric(d['bug']) > 0).map({True: 'defective', False: 'clean'})
        d = d.drop(columns=[c for c in d.columns if c in ('name', 'version', 'name.1', 'bug')])
        return d, y, 'promise ck (label = bug > 0)'
    if src in OFFICIAL_SRC:                                   # official sites and author repositories (official_sources.py)
        spec = OFFICIAL_BY_PATH[os.path.relpath(path if os.path.isabs(path) else os.path.join(HERE, path), SRC)]
        d, y = official_sources.load(spec); return d, y, f'{src} ({spec[3]})'
    raise ValueError(src)

def build():
    C = []
    def add(src, name, path):
        try:
            d, y, how = parse(src, path)
        except Exception as e:
            C.append(dict(src=src, name=name, path=path, n=None, f=None, classes=None, minority=None, dist=None, err=str(e)[:80])); return
        vc = y.value_counts()
        C.append(dict(src=src, name=name, path=os.path.relpath(path, HERE), n=len(y), f=d.shape[1], classes=len(vc),
                      minority=int(vc.min()), dist=sorted(vc.astype(int).tolist()), err=''))
    for p in sorted(glob.glob(os.path.join(SRC, 'Fuminides_keel_datasets', '*', '*.dat'))):
        add('KEEL-std(F)', os.path.basename(p)[:-4], p)
    for p in sorted(glob.glob(os.path.join(SRC, 'keelcsv_lfs', '*.csv'))):
        add('KEEL-std(C)', os.path.basename(p)[:-4], p)
    for p in sorted(glob.glob(os.path.join(SRC, 'pmlb', '*.tsv.gz'))):
        add('PMLB', os.path.basename(p)[:-7], p)
    for p in sorted(glob.glob(os.path.join(SRC, 'lpfgarcia_ucipp', 'uci', '*.arff'))):
        add('UCI++', os.path.basename(p)[:-5], p)
    for p in sorted(glob.glob(os.path.join(SRC, 'renatopp_arff-datasets', 'classification', '*.arff'))):
        add('Weka-UCI', os.path.basename(p)[:-5], p)
    for p in sorted(glob.glob(os.path.join(SRC, 'klainfo_DefectData', 'inst', 'extdata', 'terapromise', 'ck', '*.csv'))):
        add('PROMISE-ck', os.path.basename(p)[:-4], p)
    for p in sorted(glob.glob(os.path.join(SRC, 'klainfo_DefectData', 'inst', 'extdata', 'terapromise', 'mccabe', '*.arff'))):
        add('NASA-MDP', os.path.basename(p)[:-5], p)
    for p in sorted(glob.glob(os.path.join(SRC, 'jbrownlee', '*.csv'))):
        add('jbrownlee-UCI', os.path.basename(p)[:-4], p)
    for sp in official_sources.entries():                     # 8 Nov 2026 (second round): official sites, author repos
        add(sp[0], sp[1], os.path.join(SRC, sp[2]))
    c = pd.DataFrame(C); c['key'] = c.name.map(key)
    return c

if __name__ == '__main__':
    c = build()
    c.to_csv(os.path.join(HERE, 'file_catalog_ext.csv'), index=False)
    print(c.groupby('src').size()); print('errors', (c.err != '').sum()); print(c[c.err != ''][['src', 'name', 'err']].to_string())
