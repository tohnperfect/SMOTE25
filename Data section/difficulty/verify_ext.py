"""Second verification pass over the entries that could not be checked on 28 Oct 2026 (Claude, 8 Nov 2026).

Toon (8 Nov): "pull every dataset that was not yet analysed". Same definition of "verifiable" as verify.py
(difficulty/README.md), applied to the extended mirror catalog (mirrors_ext.py -> file_catalog_ext.csv):

  1. a public file is found from the dataset name (name crosswalk below: exact key, ALIAS, KEEL split names whose
     two class groups are written in the other order, or a printed KEEL split name cut at the "_vs_" boundary);
  2. the printed number of instances equals the file exactly (features may differ by 1), or the paper prints no size,
     the name is an exact/alias match and the entry is not `modified` (Toon 28 Oct);
  3. a printed minority size must equal the file (binary file) or one unique union of classes (multiclass file);
     a printed number of classes must equal the file when the task is used as is.

Only entries whose 28 Oct status was U-no_public_file, U-size_mismatch, U-task_not_reconstructible or
U-minority_mismatch are re-examined. Every other entry keeps its 28 Oct status, file and source, so the
643 entries already measured are unchanged. U-synthetic and U-no_printed_size (Toon 28 Oct, approach A) stay.

ALIAS is a name crosswalk only (other published names of the same dataset). It proposes candidate files; whether a
file is accepted is decided by rule 2-3, never by the alias. Each alias carries the reason in ALIAS_NOTE.
IMBLEARN gives the minority definition of the imbalanced-learn benchmark tasks (imbalanced-learn documentation,
`fetch_datasets`, Lemaitre, Nogueira & Aridas 2017); those tasks are rebuilt from the named source file and the
feature count may differ because imbalanced-learn one-hot encodes nominal attributes.

Input:  verifiability_entries_28oct.csv (the 28 Oct result, kept unchanged as the starting point).
Output: verifiability_entries.csv (all 1,653 entries; the 28 Oct columns + pass, basis, candidates_considered,
task_minority) -- the file every later script reads -- and verify_ext_summary.json.
"""
import re, json, os, itertools
import pandas as pd, numpy as np
from catalog import key
from mirrors_ext import parse

HERE = os.path.dirname(os.path.abspath(__file__))
RECHECK = {'U-no_public_file', 'U-size_mismatch', 'U-task_not_reconstructible', 'U-minority_mismatch'}

# corpus key -> catalog keys (other published names of the same data set)
ALIAS = {
 'balance': ['balancescale'], 'balancescale': ['balance'],
 'liver': ['bupa'], 'liverdisorders': ['bupa'], 'bupa': ['bupa'],
 'cmc': ['contraceptive', 'contraceptivemethodchoice', 'contraceptivemethod'],
 'contraceptivemethodchoice': ['contraceptive', 'cmc', 'contraceptivemethod'],
 'contraceptivel': ['contraceptive', 'contraceptivemethodchoice', 'cmc'],
 'contraceptive': ['contraceptivemethodchoice', 'cmc', 'contraceptivemethod'],
 'automobile': ['automobile', 'autos', 'deprecatedauto'], 'autos': ['automobile', 'autos', 'deprecatedauto'],
 'cleveland': ['cleveland', 'heartdiseaseprocessedcleveland', 'deprecatedcleveland'],
 'thyroid': ['thyroid', 'annthyroid'], 'ann': ['thyroid', 'annthyroid'],
 'thyroidsick': ['sick'], 'sick': ['sick'],
 'sickeuthyroid': ['thyroidsickeuthyroid'],
 'flare': ['flare', 'deprecatedsolarflare2', 'solarflare2'], 'solarflare2': ['flare', 'deprecatedsolarflare2', 'solarflare2'],
 'satellite': ['satimage', 'statloglandsatsatellite'], 'sat': ['satimage', 'statloglandsatsatellite'],
 'statlandsat': ['satimage', 'statloglandsatsatellite'], 'satimage': ['satimage', 'statloglandsatsatellite'],
 'statlog': ['satimage', 'statloglandsatsatellite', 'segment', 'segmentation', 'statlogimagesegmentation', 'shuttle',
             'german', 'statloggermancredit', 'statloggermancreditnumeric', 'heart', 'statlogheart', 'australian',
             'statlogaustraliancredit', 'vehicle', 'statlogvehiclesilhouettes'],
 'page': ['pageblocks'], 'pageblock': ['pageblocks'], 'pageblocks': ['pageblocks'],
 'hayesroth': ['hayesroth'],
 'vertebralcolumn': ['vertebracolumn3c', 'vertebracolumn2c', 'column3c', 'column2c'],
 'vertebral': ['vertebracolumn3c', 'vertebracolumn2c', 'column3c', 'column2c'],
 'vertebal': ['vertebracolumn3c', 'vertebracolumn2c', 'column3c', 'column2c'],
 'userknowledge': ['userknowledge'], 'userknowledgemodeling': ['userknowledge'], 'userknowledgemodelling': ['userknowledge'],
 'uknowledge': ['userknowledge'],
 'sensorreadings': ['robotnavsensorreadings24', 'robotnavsensorreadings4', 'robotnavsensorreadings2'],
 'robot': ['robotnavsensorreadings24', 'robotnavsensorreadings4', 'robotnavsensorreadings2'],
 'libra': ['movementlibras'], 'libras': ['movementlibras'], 'movementlibras': ['movementlibras'],
 'breasttissue': ['breasttissue6class', 'breasttissue4class'],
 'waveform': ['waveform21', 'waveformv1', 'waveform40', 'waveformv2', 'waveform5000'],
 'mammography': ['mammography'], 'oil': ['oilspill'], 'oilspill': ['oilspill'],
 'cardiotocography': ['cardiotocography3class', 'cardiotocography10class'],
 'ctg': ['cardiotocography3class', 'cardiotocography10class'], 'cardgraphy': ['cardiotocography3class', 'cardiotocography10class'],
 'banknote': ['banknoteauthentication'], 'bloodservice': ['bloodtransfusionservice'],
 'mfeatfouri': ['mfeatfourier'], 'mfzernike': ['mfeatzernike'], 'mfmorph': ['mfeatmorphological'],
 'wdbc': ['wdbc', 'breastcancerwisconsindiagnostic'], 'wpbc': ['wpbc'],
 'breastw': ['wisconsin', 'breastw', 'breastcancerwisconsin', 'breastcancerwisconsinoriginal', 'deprecatedbreastw'],
 'breastcancerwisconsin': ['wisconsin', 'breastw', 'breastcancerwisconsin', 'breastcancerwisconsinoriginal'],
 'breastcanceroriginal': ['wisconsin', 'breastw', 'breastcancerwisconsin', 'breastcancerwisconsinoriginal'],
 'breastcancer': ['breastcancer', 'breast'], 'breastc': ['breastcancer', 'breast'], 'breasty': ['breastcancer', 'breast'],
 'breast': ['breast', 'breastcancer', 'wisconsin', 'breastw'],
 'german': ['german', 'creditg', 'statloggermancredit', 'statloggermancreditnumeric', 'creditapprovalgermany'],
 'germannumer': ['statloggermancreditnumeric'], 'creditg': ['german', 'creditg', 'statloggermancredit'],
 'australian': ['australian', 'statlogaustraliancredit'], 'australia': ['australian', 'statlogaustraliancredit'],
 'heart': ['heart', 'statlogheart', 'heartstatlog'],
 'pima': ['pima', 'pimaindiansdiabetes', 'diabetes'], 'pimaindiandiabetes': ['pima', 'pimaindiansdiabetes', 'diabetes'],
 'pimadiabetes': ['pima', 'pimaindiansdiabetes', 'diabetes'], 'pid': ['pima', 'pimaindiansdiabetes', 'diabetes'],
 'diabetes': ['pima', 'pimaindiansdiabetes', 'diabetes'],
 'glassidentification': ['glass'], 'bezediris': ['iris'],
 'segment': ['segment', 'segmentation', 'statlogimagesegmentation'], 'segmentation': ['segment', 'segmentation', 'statlogimagesegmentation'],
 'imgseg': ['segment', 'segmentation', 'statlogimagesegmentation'],
 'letterrecognition': ['letter'],
 'vehicle': ['vehicle', 'statlogvehiclesilhouettes'],
 'splice': ['splice', 'molecularsplicejunction', 'dna'],
 'connect4': ['connect4'],
 'chess': ['chess', 'krvskp', 'krvsk', 'krkopt'], 'chessckingrookvsking': ['krvsk', 'krkopt'],
 'platesfaults': ['steelplatesfaults'], 'fault': ['steelplatesfaults'],
 'qsar': ['qsarbiodegradation'], 'seismicbumps': ['seismicbumps'],
 'climate': ['climatesimulationcraches'], 'climatesim': ['climatesimulationcraches'],
 'fertility': ['fertilitydiagnosis'], 'ilpd': ['indianliverpatient'], 'parkinson': ['parkinsons'],
 'planrelax': ['planningrelax'], 'planningrelax': ['planningrelax'],
 'taevaluation': ['tae', 'teachingassistantevaluation'], 'tae': ['tae', 'teachingassistantevaluation'],
 'customers': ['wholesalechannel', 'wholesaleregion'],
 'ozonelevel': ['ozoneonehr', 'ozoneeighthr'], 'anneal': ['anneal', 'annealing'],
 'spectf': ['spectf', 'spectfheart'], 'spect': ['spect', 'spectheart'],
 'carevaluation': ['car', 'carevaluation'], 'car': ['car', 'carevaluation'],
 'votes': ['housevotes', 'vote', 'voting', 'congressionalvotingrecords'],
 'postoperative': ['postoperative', 'postoperativepatient', 'postoperativepatientdata'],
 'led': ['led7digit'], 'opticaldigits': ['optdigits'], 'ocr': ['optdigits'],
 'pendigits': ['pendigits', 'penbased'], 'penbased': ['penbased', 'pendigits'], 'pendigit': ['pendigits', 'penbased'],
 'habermanssurvival': ['haberman', 'habermanssurvival'],
 'newthyroid': ['newthyroid', 'thyroidnewthyroid'], 'newthyr': ['newthyroid', 'thyroidnewthyroid'],
 'winered': ['winequalityred'], 'winequalityred': ['winequalityred'], 'winequalitywhite': ['winequalitywhite'],
 'winequality': ['winequalityred', 'winequalitywhite'],
 'abalone': ['abalone', 'abalone28class'], 'mushrooms': ['mushroom'],
 'musk': ['musk', 'clean2'], 'semeion': ['semeion'],
 'eucalyptus': [], 'svmguide1': [],
}
ALIAS_NOTE = 'UCI/KEEL/Weka/PMLB file names of the same data set (e.g. liver = bupa = liver-disorders; cmc = contraceptive method choice; satellite = satimage = statlog landsat).'

# imbalanced-learn benchmark tasks: corpus key -> (source catalog keys, minority labels, documented minority size)
IMBLEARN = {
 'satimage4': (['satimage'], ['4'], 626), 'letterimg': (['letter'], ['Z'], 734), 'opticaldigits': (['optdigits'], ['8'], 554),
 'pendigits': (['penbased', 'pendigits'], ['5'], 1055), 'thyroidsick': (['sick'], ['sick'], 231),
 'abalone19': (['abalone28class'], ['19'], 32), 'isolet': ([], [], 600), 'sickeuthyroid': (['thyroidsickeuthyroid'], ['sick'], 293),
}

def num(x):
    if pd.isna(x): return None
    m = re.search(r'\d[\d,]*', str(x)); return int(m.group().replace(',', '')) if m else None

def vs_parts(k):
    m = re.match(r'^([a-z]+?)(\d[\d]*)vs(\d[\d]*)$', k)
    return (m.group(1), frozenset([m.group(2), m.group(3)])) if m else None

def subsets(ds, t):
    if len(ds) > 14: return None
    return sum(1 for k in range(1, len(ds)) for s in itertools.combinations(range(len(ds)), k) if sum(ds[i] for i in s) == t)

SRC_RANK = {'KEEL(keel_ds)': 0, 'KEEL(imbalanced_databases)': 0, 'KEEL-std(F)': 1, 'KEEL-std(C)': 2, 'UCI++': 3, 'Weka-UCI': 4,
            'jbrownlee-UCI': 5, 'imbalanced_databases(other fmt)': 6, 'PMLB': 7, 'PROMISE-ck': 8, 'NASA-MDP': 8}

def main():
    old = pd.read_csv(os.path.join(HERE, 'verifiability_entries_28oct.csv'))   # 28 Oct snapshot (unchanged input)
    rec = pd.read_csv(os.environ.get('DATASET_RECORDS', os.path.join(HERE, '..', 'out', 'dataset_records.csv'))).set_index('record_id')
    c0 = pd.read_csv(os.path.join(HERE, 'file_catalog.csv')); c0['dist'] = c0.dist.map(lambda s: json.loads(s) if isinstance(s, str) else None)
    c1 = pd.read_csv(os.path.join(HERE, 'file_catalog_ext.csv')); c1['dist'] = c1.dist.map(lambda s: json.loads(s) if isinstance(s, str) else None)
    # PMLB rows of the old catalog have no class counts; the ext catalog parses every PMLB file, so use ext for PMLB
    c0 = c0[c0.src != 'PMLB']
    cat = pd.concat([c0.assign(origin='28oct'), c1.assign(origin='ext')], ignore_index=True)
    cat = cat[cat.n.notna()]
    cat = cat[~((cat.classes > 0.3 * cat.n) | (cat.classes > 60))]           # unusable target column in the mirror
    cat['key2'] = cat.key.str.replace('vs', '')
    cat['rank'] = cat.src.map(SRC_RANK).fillna(9)
    cat['vsp'] = cat.key.map(vs_parts)

    def candidates(r):
        ks = {key(r['name'])}
        try: ks.add(key(rec.loc[r.record_id, 'name_as_reported']))
        except Exception: pass
        out = []
        for k in ks:
            for _, x in cat[cat.key == k].iterrows(): out.append((x, 'exact name'))
            for _, x in cat[cat.key2 == k.replace('vs', '')].iterrows(): out.append((x, 'exact name (vs dropped)'))
            for a in ALIAS.get(k, []):
                for _, x in cat[cat.key == a].iterrows(): out.append((x, 'alias'))
            vp = vs_parts(k)
            if vp:
                for _, x in cat[cat.vsp == vp].iterrows(): out.append((x, 'KEEL split, class groups in the other order'))
            if re.search(r'\d$', k) and len(k) >= 6:
                for _, x in cat[cat.key.str.startswith(k + 'vs')].iterrows(): out.append((x, 'KEEL split name cut at _vs_'))
        seen = set(); uniq = []
        for x, b in out:
            idk = (x.src, x['name'])
            if idk not in seen: seen.add(idk); uniq.append((x, b))
        return uniq

    # One copy per data set: several mirrors hold the same file (e.g. KEEL bupa and UCI++ bupa). Among files with the same
    # number of rows, features and class counts, an entry is mapped to the best-ranked source (SRC_RANK; KEEL with
    # header first, PMLB last because it label-encodes nominal attributes), ties -> the copy already used on 28 Oct,
    # so that one data set does not become two measured tasks in the 8 Nov pass.
    used28 = set(zip(old[old.verif.str.startswith('V-')].file, old[old.verif.str.startswith('V-')].file_src))
    cat['sig'] = [(int(a), int(b), str(c)) for a, b, c in zip(cat.n, cat.f, cat.dist)]
    def canon(x):
        same = cat[cat.sig == (int(x.n), int(x.f), str(x.dist))]
        if len(same) <= 1: return x
        same = same.assign(u=[0 if (a, b) in used28 else 1 for a, b in zip(same['name'], same.src)])
        return same.sort_values(['rank', 'u']).iloc[0]   # source rank first (PMLB last: nominal attributes label-encoded)

    rows = []
    for _, r in old.iterrows():
        row = r.to_dict(); row.update(pass_='28oct', basis='', candidates_considered='')
        if r.verif not in RECHECK:
            rows.append(row); continue
        q = rec.loc[r.record_id]
        pn, pf, pc, pm = num(q.n_instances), num(q.n_features), num(q.n_classes), num(q.n_minority)
        cat_ = r.category
        cands = candidates(r)
        row['pass_'] = 'ext'
        row['candidates_considered'] = '; '.join(f"{x.src}:{x['name']}({int(x.n)})" for x, _ in cands)[:400]
        k = key(r['name'])
        # imbalanced-learn tasks (source names imbalanced-learn)
        if k in IMBLEARN and 'imbalanced' in str(r.source).lower():
            srcs, labs, nminDoc = IMBLEARN[k]
            hit = [x for x in cat.itertuples() if x.key in srcs and x.origin == 'ext' and (pn is None or x.n == pn)]
            good = []
            for x in sorted(hit, key=lambda z: z.rank):
                _, yy, _ = parse(x.src, os.path.join(HERE, x.path))
                if int(yy.isin(labs).sum()) == nminDoc: good.append(x)
            if good and labs:
                x = good[0]
                row.update(verif='V-imblearn_task', file=x.name, file_src=x.src, file_n=x.n, file_f=x.f, task_minority='+'.join(labs),
                           basis=f'imbalanced-learn task: minority = {"+".join(labs)} (documented size {nminDoc})',
                           note_structure='imbalanced-learn task rebuilt from the named source file; feature count may differ (one-hot)')
            else:
                row.update(verif='U-no_public_file', basis='imbalanced-learn task, source file not in any mirror')
            rows.append(row); continue
        if not cands:
            row.update(verif='U-no_public_file', basis='no file under this name or its aliases in any mirror'); rows.append(row); continue
        if pn is None:
            ok = [(x, b) for x, b in cands if b in ('exact name', 'alias', 'exact name (vs dropped)')]
            if cat_ == 'modified' or not ok:
                row.update(verif='U-no_printed_size' if cat_ == 'modified' else 'U-no_public_file',
                           basis='paper prints no size' + (' and the entry is modified (Toon 28 Oct)' if cat_ == 'modified' else '; only a loose name match'))
                rows.append(row); continue
            # prefer the source the paper names
            s = str(r.source).lower()
            def pref(x):
                return (0 if ('keel' in s and x.src.startswith('KEEL')) or ('uci' in s and x.src in ('UCI++', 'Weka-UCI', 'jbrownlee-UCI')) else 1, x['rank'])
            exact = [t for t in ok if t[1] != 'alias']
            ok = exact or ok                                   # an alias is used only when no file has the exact name
            best = min(pref(t[0])[0] for t in ok)
            ok = [t for t in ok if pref(t[0])[0] == best]
            if len({(int(t[0].n), str(t[0].dist)) for t in ok}) > 1:
                row.update(verif='U-name_ambiguous', basis='no printed size; the name fits files with different structure: ' +
                           ', '.join(sorted({f"{t[0]['name']}({int(t[0].n)})" for t in ok})))
                rows.append(row); continue
            x, b = sorted(ok, key=lambda t: pref(t[0]))[0]
            x = canon(x)
            if pc is not None and pc != x.classes and not (pc == 2):
                row.update(verif='U-size_mismatch', basis=f'no printed size; printed classes {pc} != file {int(x.classes)}'); rows.append(row); continue
            if pc == 2 and x.classes != 2:
                row.update(verif='U-task_not_reconstructible', basis='no printed size; two-class task from a multiclass file, minority not printed'); rows.append(row); continue
            row.update(verif='V-name_only_ext', file=x['name'], file_src=x.src, file_n=x.n, file_f=x.f, basis=b,
                       note_structure='paper reports only the dataset name; structure taken from the named file')
            rows.append(row); continue
        ex = [(x, b) for x, b in cands if int(x.n) == pn]
        if not ex:
            near = sorted(cands, key=lambda t: abs(t[0].n - pn))[0][0]
            row.update(verif='U-size_mismatch', file=near['name'], file_src=near.src, file_n=near.n, file_f=near.f,
                       basis=f'printed N {pn}; nearest file {near.src}:{near["name"]} N {int(near.n)}'); rows.append(row); continue
        if pf is not None:
            exf = [(x, b) for x, b in ex if abs(int(x.f) - pf) <= 1]
            if not exf:
                x = ex[0][0]
                row.update(verif='U-size_mismatch', file=x['name'], file_src=x.src, file_n=x.n, file_f=x.f,
                           basis=f'N matches but printed features {pf} vs file {int(x.f)}'); rows.append(row); continue
            ex = exf
        ex = sorted(ex, key=lambda t: t[0]['rank'])
        decided = None
        for x, b in ex:
            ds = x.dist
            if ds is None: continue
            if len(ds) == 2:
                if pm is None or pm == ds[0]: decided = ('V-binary_file', x, b); break
                decided = decided or ('U-minority_mismatch', x, b); continue
            if pc == len(ds) and (pm is None or pm == ds[0]):           # same rule as verify.py (28 Oct)
                decided = ('V-multiclass_asis', x, b); break
            if pm is not None:
                kk = subsets(ds, pm)
                if kk == 1: decided = ('V-binarized_rule_unique', x, b); break
                decided = decided or (('V?-binarized_rule_ambiguous' if kk and kk > 1 else 'U-task_not_reconstructible'), x, b)
            else:
                decided = decided or ('U-task_not_reconstructible', x, b)
        if decided is None:
            row.update(verif='U-no_class_info', basis='file has no class counts'); rows.append(row); continue
        v, x, b = decided
        x = canon(x)
        row.update(verif=v, file=x['name'], file_src=x.src, file_n=x.n, file_f=x.f, basis=b)
        rows.append(row)
    o = pd.DataFrame(rows).rename(columns={'pass_': 'pass'})
    o.to_csv(os.path.join(HERE, 'verifiability_entries.csv'), index=False)       # current file read by every later script
    newV = o[(o['pass'] == 'ext') & o.verif.str.startswith('V-')]
    allV = o[o.verif.str.startswith('V-')]
    summ = dict(entries=len(o), rechecked=int((o['pass'] == 'ext').sum()),
                status_28oct=old.verif.value_counts().to_dict(), status_now=o.verif.value_counts().to_dict(),
                newly_verifiable=dict(entries=len(newV), papers=int(newV.paper.nunique()), names=int(newV['name'].nunique()),
                                      files=int(newV.file.nunique()), by_source=newV.file_src.value_counts().to_dict(),
                                      by_basis=newV.basis.value_counts().to_dict(), by_status=newV.verif.value_counts().to_dict()),
                verifiable_total=dict(entries=len(allV), papers=int(allV.paper.nunique()), names=int(allV['name'].nunique()), files=int(allV.file.nunique())))
    json.dump(summ, open(os.path.join(HERE, 'verify_ext_summary.json'), 'w'), indent=1, default=int)
    print(json.dumps(summ, indent=1, default=int))

if __name__ == '__main__':
    main()
