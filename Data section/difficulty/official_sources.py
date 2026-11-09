"""Official-site and author-repository files (8 Nov 2026, Claude; Toon: "the remaining ~200 names come from public
benchmarks, download them"). Added to the extended catalog by mirrors_ext.build(); parsed by mirrors_ext.parse().

Sources (files in src/, not stored in git; how to fetch them again: fetch_mirrors_ext.sh and official_manifest.csv)
  UCI-official     archive.ics.uci.edu/static/public/<id>/<name>.zip   fetched in the browser on Toon's machine (the
                   site is not reachable from the cloud workspace), unpacked by unbundle_official.py into src/official/uci/
  LibSVM           www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/    same route, src/official/libsvm/
  author-HDE       github.com/smallcube/HD-Ensemble  datasets/*.arff  (HDE paper's own processed sets, sparse ARFF)
  author-DGOT      github.com/MLneuers/DGOT  datasets/abalone_15/abalone_15.csv
  author-SOS       github.com/JayoungKim408/SOS  tabular_datasets/*.npz (train + test arrays, label = last column)
  author-MBS       github.com/b10071007/Model-Based-Synthetic-Sampling  data/*/<Name>_data.csv (label = first column)
  (mafalda: github.com/sisinflab-swot/mafalda was checked; not loadable as the EMDO task, see below)
  author-kmeans    github.com/felix-last/evaluate-kmeans-smote release v0.0.1 uci_extended.tar.gz (the k-means SMOTE
                   paper: "All modified and simulated datasets used in the study are made available at ...")
Commits of the author repositories are in official_manifest.csv.

Each entry of SPEC: (src, catalog name, path under src/, loader, options). A loader returns (features DataFrame of
strings/categories, labels Series of str). Nothing here decides whether a file is the one a paper used: verify_ext.py
applies the same rule as before (printed size must match the file).
"""
import os, re, glob, csv, io
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

def _clean(d):
    return d.apply(lambda s: s.astype(str).str.strip().str.strip("'\""))

def arff_any(path, class_attr=None):
    """dense or sparse ARFF ({index value, ...} rows; absent index = 0)."""
    names, nom, rows, data = [], set(), [], False
    for ln in open(path, errors='ignore'):
        l = ln.strip()
        if not l or l.startswith('%'): continue
        if data:
            if l.startswith('{'):
                r = ['0'] * len(names)
                for kv in l.strip('{}').split(','):
                    kv = kv.strip()
                    if not kv: continue
                    i, v = kv.split(None, 1); r[int(i)] = v.strip()
                rows.append(r)
            else:
                rows.append([x.strip() for x in next(csv.reader([l], skipinitialspace=True))])
        elif l.lower().startswith('@attribute'):
            m = re.match(r"@attribute\s+('([^']*)'|\"([^\"]*)\"|(\S+))\s*(.*)", l, re.I)
            nm = m.group(2) or m.group(3) or m.group(4); names.append(nm)
            if m.group(5).strip().startswith('{'): nom.add(nm)
        elif l.lower().startswith('@data'): data = True
    rows = [r for r in rows if len(r) == len(names)]
    d = pd.DataFrame(rows, columns=names)
    cls = class_attr if class_attr in names else ([n for n in names if n.strip().lower() in ('class', 'label', 'target')] or [names[-1]])[0]
    y = d.pop(cls).astype(str).str.strip().str.strip("'\""); nom.discard(cls)
    d = _clean(d)
    return d.assign(**{c: d[c].astype('category') for c in nom if c in d}), y

def libsvm(paths):
    """one or more LibSVM files (train [+ test]) -> dense frame (absent index = 0)."""
    ys, rows, mx = [], [], 0
    for p in paths:
        for ln in open(p):
            t = ln.split()
            if not t: continue
            ys.append(t[0]); r = {}
            for kv in t[1:]:
                i, v = kv.split(':'); r[int(i)] = v; mx = max(mx, int(i))
            rows.append(r)
    d = pd.DataFrame([[r.get(i, '0') for i in range(1, mx + 1)] for r in rows], columns=[f'f{i}' for i in range(1, mx + 1)])
    return d, pd.Series(ys).astype(str)

def table(path, sep=',', header='infer', label=-1, drop=(), na=None, sheet=None, skiprows=None, onehot_last=None, names=None, encoding=None,
          literal=False):
    # literal=True: read every cell as written; pandas would otherwise turn words such as 'None' or 'NA' into missing values
    # (9 Nov: the IBM Sales Win Loss file uses 'None' as one of the three values of Competitor Type)
    if path.endswith(('.xls', '.xlsx')):
        d = pd.read_excel(path, sheet_name=sheet or 0, header=0 if header == 'infer' else header, dtype=str, skiprows=skiprows)
    else:
        d = pd.read_csv(path, sep=sep, header=0 if header == 'infer' else header, dtype=str, skipinitialspace=True,
                        engine='python' if sep not in (',', '\t', ';') else 'c', skiprows=skiprows, encoding=encoding,
                        keep_default_na=not literal)
    if header is None: d.columns = names or [f'a{i}' for i in range(d.shape[1])]
    d = d.drop(columns=[c for c in drop if c in d.columns])
    if onehot_last:                                      # class given as k one-hot columns at the end (steel plates faults)
        oh = d.iloc[:, -onehot_last:].astype(float).values; d = d.iloc[:, :-onehot_last]
        assert (oh.sum(1) == 1).all(), 'STOP: one-hot class columns do not sum to 1'
        return _clean(d), pd.Series([(names or [])[-onehot_last + i] if names else f'class{i + 1}' for i in oh.argmax(1)])
    lab = d.columns[label] if isinstance(label, int) else label
    y = d.pop(lab).astype(str).str.strip().str.strip("'\"")
    d = _clean(d)
    if na is not None: d = d.replace(na, np.nan)
    return d, y

def npz_traintest(path):
    z = np.load(path, allow_pickle=False)                      # never unpickle downloaded files
    a = np.vstack([z['train'], z['test']])
    return pd.DataFrame(a[:, :-1]).astype(str), pd.Series(a[:, -1]).astype(str)

def cluto(path):
    """CLUTO sparse matrix (first line: rows cols nonzeros; then per row 'col value' pairs, 1-based) + <path>.rclass labels
    (9 Nov 2026). Returned as a sparse frame, so that the catalog gets the true shape without a dense copy."""
    from scipy import sparse
    rows, cols, vals = [], [], []
    with open(path) as fh:
        nr, nc, _ = map(int, fh.readline().split())
        for i, ln in enumerate(fh):
            t = ln.split()
            for j in range(0, len(t) - 1, 2):
                rows.append(i); cols.append(int(t[j]) - 1); vals.append(float(t[j + 1]))
    m = sparse.csr_matrix((vals, (rows, cols)), shape=(nr, nc))
    y = pd.Series(open(path + '.rclass').read().split()).astype(str)
    assert len(y) == nr, 'STOP: CLUTO label count differs from rows'
    # pandas 3 gives the sparse frame a NaN fill value (pandas 2: 0); a cell absent from the CLUTO file is a zero count,
    # so the fill value is set to 0 explicitly (9 Nov)
    return pd.DataFrame.sparse.from_spmatrix(m).fillna(0.0), y

def dirconcat(folder, label=-1):
    """all files of one folder, no header, label = given column (9 Nov 2026; UCI 'healthy older people' room files)."""
    fs = sorted(f for f in glob.glob(os.path.join(SRC, folder, '*')) if os.path.isfile(f) and not f.lower().endswith('.txt'))
    d = pd.concat([pd.read_csv(f, header=None) for f in fs], ignore_index=True)
    y = d.pop(d.columns[label]).astype(str).str.strip()
    return _clean(d), y

def load(spec):
    src, name, rel, fn, kw = spec
    p = os.path.join(SRC, rel)
    if fn == 'arff': return arff_any(p, **kw)
    if fn == 'libsvm': return libsvm([os.path.join(SRC, r) for r in kw['files']])
    if fn == 'table': return table(p, **kw)
    if fn == 'npz': return npz_traintest(p)
    if fn == 'cluto': return cluto(p)
    if fn == 'dirconcat': return dirconcat(rel, **kw)
    if fn == 'concat':                                          # several table files of one data set (train + test splits)
        parts = [table(os.path.join(SRC, r), **kw.get('opts', {})) for r in kw['files']]
        return pd.concat([d for d, _ in parts], ignore_index=True), pd.concat([y for _, y in parts], ignore_index=True)
    raise ValueError(fn)

A = 'author'
SPEC = []
# --- author repositories -------------------------------------------------------------------------------------------
for f in sorted(glob.glob(os.path.join(SRC, A, 'HD-Ensemble', '*.arff'))):
    SPEC.append(('author-HDE', os.path.basename(f)[:-5], os.path.relpath(f, SRC), 'arff', {}))
SPEC += [
 ('author-DGOT', 'abalone_15', f'{A}/DGOT/abalone_15.csv', 'table', dict(label=-1)),
 ('author-SOS', 'default', f'{A}/SOS/default.npz', 'npz', {}),
 ('author-SOS', 'shoppers', f'{A}/SOS/shoppers.npz', 'npz', {}),
 ('author-SOS', 'satimage', f'{A}/SOS/satimage.npz', 'npz', {}),
 ('author-MBS', 'bank', f'{A}/MBS/bank/Bank_data.csv', 'table', dict(label='Label')),
 ('author-MBS', 'hmeq', f'{A}/MBS/hmeq/Hmeq_data.csv', 'table', dict(label='Label')),
 ('author-MBS', 'give me some credit', f'{A}/MBS/Give Me Some Credit/Credit_data.csv', 'table', dict(label='Label')),
 ('author-MBS', 'promotion', f'{A}/MBS/promotion/Promotion_data.csv', 'table', dict(label='Label')),
]
# mafalda (EMDO): the repository holds 4 semicolon CSV files (24,953 rows, 3 label columns); EMDO prints 23,762 x 14 and does
# not say how the files were combined or which rows were dropped, so the task cannot be rebuilt (recorded, not loaded).
# k-means SMOTE release (uci_extended.tar.gz, sha256 in official_manifest.csv): only the modified versions (name ends in the
# imbalance ratio, e.g. pima2) and the simulated sets; the unmodified base files (pima, iris, ...) are left out so that they
# do not replace the standard files of other papers. One file is gzip inside .csv (breast_tissue), not used.
for f in sorted(glob.glob(os.path.join(SRC, A, 'kmeans', '*.csv'))):
    nm = os.path.basename(f)[:-4]
    if re.search(r'\d$', nm):
        SPEC.append(('author-kmeans', nm, os.path.relpath(f, SRC), 'table', dict(label=-1, encoding='latin-1')))
# --- LibSVM -----------------------------------------------------------------------------------------------------------
L = 'official/libsvm'
SPEC += [
 ('LibSVM', 'fourclass', f'{L}/binary__fourclass', 'libsvm', dict(files=[f'{L}/binary__fourclass'])),
 ('LibSVM', 'svmguide1', f'{L}/binary__svmguide1', 'libsvm', dict(files=[f'{L}/binary__svmguide1'])),
 ('LibSVM', 'svmguide1 (train+test)', f'{L}/binary__svmguide1+t', 'libsvm', dict(files=[f'{L}/binary__svmguide1', f'{L}/binary__svmguide1.t'])),
 ('LibSVM', 'svmguide3', f'{L}/binary__svmguide3', 'libsvm', dict(files=[f'{L}/binary__svmguide3'])),
 ('LibSVM', 'svmguide3 (train+test)', f'{L}/binary__svmguide3+t', 'libsvm', dict(files=[f'{L}/binary__svmguide3', f'{L}/binary__svmguide3.t'])),
 ('LibSVM', 'svmguide2', f'{L}/multiclass__svmguide2', 'libsvm', dict(files=[f'{L}/multiclass__svmguide2'])),
 ('LibSVM', 'a1a', f'{L}/binary__a1a', 'libsvm', dict(files=[f'{L}/binary__a1a'])),
]
# --- UCI official (filled in after the browser download; see UCI list below) -------------------------------------------
U = 'official/uci'
# (catalog name, path under src/official/uci, loader, options). Catalog names are written so that their key matches the
# corpus name (verify_ext.ALIAS adds the other spellings). Label = the class attribute named in the UCI page; columns that
# are row ids or copies of the label are dropped (listed per file). Only files that a corpus entry could use are listed.
UCI = [
 ('avila', '459_avila.zip', 'concat', dict(files=['459_avila.zip.d/avila/avila-tr.txt', '459_avila.zip.d/avila/avila-ts.txt'], opts=dict(header=None))),
 ('avila train', '459_avila.zip.d/avila/avila-tr.txt', 'table', dict(header=None)),
 ('covertype', '31_covertype.zip.d/covtype.data.gz', 'table', dict(header=None)),
 ('phishingdata', '379_website+phishing.zip.d/PhishingData.arff', 'arff', dict(class_attr='Result')),
 ('online shoppers', '468_online+shoppers+purchasing+intention+dataset.zip.d/online_shoppers_intention.csv', 'table', dict(label='Revenue')),
 *[(f'polish bankruptcy year{i}', f'365_polish+companies+bankruptcy+data.zip.d/{i}year.arff', 'arff', dict(class_attr='class')) for i in range(1, 6)],
 ('taiwanese bankruptcy', '572_taiwanese+bankruptcy+prediction.zip.d/data.csv', 'table', dict(label='Bankrupt?')),
 ('firewall', '542_internet+firewall+data.zip.d/log2.csv', 'table', dict(label='Action')),
 ('htru2', '372_htru2.zip.d/HTRU_2.arff', 'arff', {}),
 ('isolet', '54_isolet.zip', 'concat', dict(files=['54_isolet.zip.d/isolet1+2+3+4.data', '54_isolet.zip.d/isolet5.data'], opts=dict(header=None))),
 ('absenteeism at work', '445_absenteeism+at+work.zip.d/Absenteeism_at_work.csv', 'table', dict(sep=';', label='Absenteeism time in hours', drop=('ID',))),
 ('drybean', '602_dry+bean+dataset.zip.d/DryBeanDataset/Dry_Bean_Dataset.arff', 'arff', dict(class_attr='Class')),
 ('hcv', '571_hcv+data.zip.d/hcvdat0.csv', 'table', dict(label='Category', drop=('Unnamed: 0', '')),),
 ('obs', '404_burst+header+packet+bhp+flooding+attack+on+optical+burst+switching+obs+network.zip.d/OBS-Network-DataSet_2_Aug27.arff', 'arff', dict(class_attr='Class')),
 ('students dropout', '697_predict+students+dropout+and+academic+success.zip.d/data.csv', 'table', dict(sep=';', label='Target')),
 ('ai4i2020', '601_ai4i+2020+predictive+maintenance+dataset.zip.d/ai4i2020.csv', 'table',
  dict(label='Machine failure', drop=('UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF'))),   # ids + the 5 failure-mode flags (parts of the label)
 ('raisin', '850_raisin.zip.d/Raisin_Dataset.zip.d/Raisin_Dataset/Raisin_Dataset.arff', 'arff', dict(class_attr='Class')),
 ('maternal', '863_maternal+health+risk.zip.d/Maternal Health Risk Data Set.csv', 'table', dict(label='RiskLevel')),
 ('occupancy training', '357_occupancy+detection.zip.d/datatraining.txt', 'table', dict(label='Occupancy', drop=('date',))),
 ('occupancy test', '357_occupancy+detection.zip.d/datatest.txt', 'table', dict(label='Occupancy', drop=('date',))),
 ('occupancy test2', '357_occupancy+detection.zip.d/datatest2.txt', 'table', dict(label='Occupancy', drop=('date',))),
 ('cnae', '233_cnae+9.zip.d/CNAE-9.data', 'table', dict(header=None, label=0)),
 ('darwin', '732_darwin.zip.d/data.csv', 'table', dict(label='class', drop=('ID',))),
 ('toxicity', '728_toxicity-2.zip.d/data.csv', 'table', dict(label='Class')),
 ('gender', '852_gender+gap+in+spanish+wp.zip.d/data.csv', 'table', dict(label='gender')),
 ('obesity', '544_estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition.zip.d/ObesityDataSet_raw_and_data_sinthetic.csv', 'table', dict(label='NObeyesdad')),
 ('rt-iot', '942_rt-iot2022.zip.d/RT_IOT2022', 'table', dict(label='Attack_type', drop=('Unnamed: 0', ''))),
 ('steel plates faults 7class', '198_steel+plates+faults.zip.d/Faults.NNA', 'table',
  dict(sep='\t', header=None, onehot_last=7, names=None)),
]
def _uci(kw):
    kw = dict(kw)
    if 'files' in kw: kw['files'] = [f'{U}/{f}' for f in kw['files']]
    return kw
SPEC += [('UCI-official', n, f'{U}/{r}' + ('+concat' if fn == 'concat' else ''), fn, _uci(kw)) for n, r, fn, kw in UCI]

# --- Kaggle (8 Nov 2026, Toon logged in to Kaggle in the in-app browser; zips downloaded from the dataset pages,
# sha256 in official_manifest.csv). Label = the target the Kaggle page names; id / index columns dropped.
KG = 'official/kaggle'
SPEC += [
 ('Kaggle', 'aids 50000', f'{KG}/aadarshvelu__aids-virus-infection-prediction/AIDS_Classification_50000.csv', 'table', dict(label='infected')),
 ('Kaggle', 'aids 15000', f'{KG}/aadarshvelu__aids-virus-infection-prediction/AIDS_Classification_15000.csv', 'table', dict(label='infected')),
 ('Kaggle', 'aids 5000', f'{KG}/aadarshvelu__aids-virus-infection-prediction/AIDS_Classification_5000.csv', 'table', dict(label='infected')),
 ('Kaggle', 'drug200', f'{KG}/prathamtripathi__drug-classification/drug200.csv', 'table', dict(label='Drug')),
 ('Kaggle', 'cardiovascular', f'{KG}/sulianova__cardiovascular-disease-dataset/cardio_train.csv', 'table', dict(sep=';', label='cardio', drop=('id',))),
 ('Kaggle', 'employee', f'{KG}/tawfikelmetwally__employee-dataset/Employee.csv', 'table', dict(label='LeaveOrNot')),
 ('Kaggle', 'ibm hr attrition', f'{KG}/pavansubhasht__ibm-hr-analytics-attrition-dataset/WA_Fn-UseC_-HR-Employee-Attrition.csv', 'table',
  dict(label='Attrition', drop=('EmployeeNumber',), encoding='utf-8-sig')),
 ('Kaggle', 'airline satisfaction train', f'{KG}/teejmahal20__airline-passenger-satisfaction/train.csv', 'table', dict(label='satisfaction', drop=('Unnamed: 0', 'id'))),
 ('Kaggle', 'smoke detection', f'{KG}/deepcontractor__smoke-detection-dataset/smoke_detection_iot.csv', 'table', dict(label='Fire Alarm', drop=('Unnamed: 0',))),
 ('Kaggle', 'telco customer churn', f'{KG}/blastchar__telco-customer-churn/WA_Fn-UseC_-Telco-Customer-Churn.csv', 'table', dict(label='Churn', drop=('customerID',))),
 ('Kaggle', 'har test', f'{KG}/uciml__human-activity-recognition-with-smartphones/test.csv', 'table', dict(label='Activity', drop=('subject',))),
]

# --- 9 Nov 2026 (Toon: "ทำต่อให้เสร็จเลย", the names that had a public file but had not been tried) ---------------------
# UCI (browser bundle, official_manifest.csv tag uci), CLUTO text collections (papers.karypis.org mirror of the glaros page,
# tag cluto), Kaggle (downloaded with Toon's sign-in). Files that were found but cannot carry the paper's task (no class
# label, regression target, time series) are recorded in verify_ext.py FOUND_NOT_USABLE instead of being loaded here.
UO = 'official/uci'
SPEC += [
 ('UCI-official', 'healthy older people1', f'{UO}/427_activity+recognition+with+healthy+older+people+using+a+batteryless+wearable+sensor.zip.d/S1_Dataset', 'dirconcat', dict(label=-1)),
 ('UCI-official', 'healthy older people2', f'{UO}/427_activity+recognition+with+healthy+older+people+using+a+batteryless+wearable+sensor.zip.d/S2_Dataset', 'dirconcat', dict(label=-1)),
 ('UCI-official', 'gender by name', f'{UO}/591_gender+by+name.zip.d/name_gender_dataset.csv', 'table', dict(label='Gender')),
 ('CLUTO', 'k1b', 'official/cluto/datasets.d/k1b.mat', 'cluto', {}),
 ('CLUTO', 'la12', 'official/cluto/datasets.d/la12.mat', 'cluto', {}),
 ('Kaggle', 'sales win loss', f'{KG}/thatbrock__ibm-watson-saleswinloss/WA_Fn-UseC_-Sales-Win-Loss.csv', 'table', dict(label='Opportunity Result', drop=('Opportunity Number',), literal=True)),
 ('Kaggle', 'creditcard', f'{KG}/mlg-ulb__creditcardfraud/creditcard.csv', 'table', dict(label='Class')),
]

def entries():
    # a spec is usable when all its files exist (path s[2] is the catalog key; '+t' marks a train+test combination)
    return [s for s in SPEC if all(os.path.exists(os.path.join(SRC, f)) for f in (s[4].get('files') or [s[2]]))]
