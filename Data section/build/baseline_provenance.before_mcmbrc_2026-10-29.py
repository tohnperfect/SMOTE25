"""baseline_provenance.py  Analysis B (19 ต.ค. 2026): ที่มาของค่า SMOTE baseline และความเทียบกันได้

อ่าน   ai-draft/full/<key>.json (smote_in_baselines, results_granularity), out/verified_outcomes.csv, out/outcome_dataset_links.csv,
       out/dataset_records.csv, PDF ผ่าน out/pdf_map.json (ตรวจทุก quote ว่ามีอยู่จริง)
เขียน  out/baseline_provenance_papers.csv   1 แถวต่อ paper ที่มี SMOTE เป็น baseline (57)
       out/baseline_identical_values.csv     คู่ paper ที่ค่าในตารางผลซ้ำกัน (สแกนทุกคู่ใน 835 แถว)
       out/baseline_provenance_summary.json

สามมิติแยกกัน (ไม่ยุบเป็นป้ายเดียว)
  provenance  B1 same study, SMOTE implementation/configuration described
              B2 same study presumed (scores in one table under one described protocol), how SMOTE was run not found
              B3 previously published scores imported (stated by the authors)
              B4 scores identical to another corpus paper's published table; the paper does not say whether they were re-run
  dataset_equivalence / protocol_equivalence  ระดับ paper ดูคอลัมน์ในไฟล์
หลักฐาน B1/B3 = ข้อความสั้นที่ตรวจกับ PDF; B4 = การเทียบตัวเลขในไฟล์นี้ (ไม่ใช่ข้อกล่าวหาว่าลอก)
"""
import csv, glob, itertools, json, os, re, subprocess, sys, unicodedata
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE); sys.path.insert(0, "build")
import reconcile_counts as RC
from analyse_dataset_usage import norm
P2PDF = {"DSRBF / Static-SMOTE": "DSRBF", "EasyEnsemble / BalanceCascade": "EasyEnsemble", "RACOG / wRACOG": "RACOG", "SMOTE-ENN / SMOTE-Tomek": "SMOTE-ENN",
         "k-means SMOTE": "k-means-SMOTE", "RBBoost / Random Balance": "RBBoost", "Survey: Stop Oversampling": "Stop-Oversampling"}
CONFIG = {  # paper: (quote, file 'main'/'supp')  SMOTE implementation or configuration described
 "A-SUWO": ("The techniques were implemented using Matlab", "main"), "AB-SMOTE": ("2.0: SMOTE k=5", "main"),
 "ADASYN": ("For both SMOTE and ADASYN, we set the number of nearest neighbors K = 5", "main"), "AMDO": ("using the KEEL software tool", "main"),
 "CBHSID": ("All approaches are used with default parameters", "main"), "CISO": ("under the same protocol", "main"),
 "DGOT": ("package is utilized to implement these benchmark methods", "main"),
 "EasyEnsemble / BalanceCascade": ("The settings of SMOTE are the same as that of SMOTEBoost (k = 5)", "main"),
 "FW-SMOTE": ("The SMOTE, BL-SMOTE, and SL-SMOTE variants were implemented in Matlab", "main"),
 "G-SMOTE": ("The implementation of the classifiers and standard oversampling algorithms was based on the Python libraries", "main"),
 "GDO": ("All the oversampling algorithms are implemented by imblearn", "main"), "GOIO": ("These three methods are implemented using the", "main"),
 "MC-CCR": ("k-nearest neighbors = 5; oversampling ratio", "main"),
 "MC-NCLWO": ("All sampling techniques and classifiers in this study are implemented in Python using the Imbalanced-learn and Scikit-learn libraries", "main"),
 "MDO": ("the nearest neighbour parameter K is set to 5 in all methods", "main"),
 "MLOS": ("SMOTE, ADASYN, Borderline-SMOTE and MWMOTE are provided in the imblearn library", "main"),
 "MWMOTE": ("For SMOTE and ADASYN, the value of the nearest neighbors, k, is set to 5", "main"),
 "NROMM": ("SMOTE-all [12] k-nearest neighbors = 5", "supp"), "OVO-SMOTE": ("All these algorithms are available within the KEEL software tool", "main"),
 "RBBoost / Random Balance": ("Weka [40] was used for the experiments", "main"),
 "RBO": ("the implementations of the reference methods provided in the imbalanced-learn [57] library were used", "main"),
 "SMOM": ("mean ranks of SMOTE (k=12)", "main"),
 "SMOTE-ENN / SMOTE-Tomek": ("Our implementation of the k-NN algorithm uses the Heterogeneous Value Difference Metric", "main"),
 "SOUP": ("All experiments were performed in the WEKA framework", "main"),
 "SPE": ("All aforementioned re-sampling methods were implemented using imbalanced-learn Python package", "main"),
}
IMPORTED = {"QC-SMOTE": ("To maintain comparability with the VS-SMOTE benchmark, we retain the published CatBoost baselines", "main",
                         "VS-SMOTE (not in the corpus)", "stated: same 30 data sets with the VS-SMOTE identifiers D1-D30",
                         "aims at comparability; equality of folds/protocol with the source not shown")}
EARLIER_SOURCE = {"AMDO": "EMDO (2021) states its data sets are those of AMDO [43]; AMDO is the earlier publication (cited by EMDO as [43])"}
SAME_DATA_STATED = {"EMDO": ("The data sets used in the simulation are the same as those used in [43]", "main")}
PM = json.load(open("out/pdf_map.json", encoding="utf-8"))
def nz(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s).replace("ﬁ", "fi").replace("ﬀ", "ff")).lower()
_pc = {}
def find(paper, quote, which):
    pk = P2PDF.get(paper, paper); m = PM[pk]; f = m["main"] if which == "main" else m["supp"][0]
    if f not in _pc: _pc[f] = subprocess.run(["pdftotext", f, "-"], capture_output=True, text=True).stdout.split("\f")
    pg = [i for i, t in enumerate(_pc[f], 1) if nz(quote) in nz(t)]
    if not pg: sys.exit(f"STOP: quote not found for {paper}: {quote}")
    return f"{'main' if which == 'main' else 'supplement'} PDF p.{','.join(map(str, pg))}"
F = {}
for f in glob.glob("ai-draft/full/*.json"):
    j = json.load(open(f, encoding="utf-8")); F[j["key"]] = j
O = list(csv.DictReader(open("out/verified_outcomes.csv", encoding="utf-8-sig")))
LK = list(csv.DictReader(open("out/outcome_dataset_links.csv", encoding="utf-8")))
DR = {d["record_id"]: d for d in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig"))}
CROSS = {k for k, v in RC.CROSS_TABLE_REVIEW.items() if v.startswith("cross-table")}
def part(o):
    if RC.AGG_RE.match(o["dataset"] or ""): return "excluded: aggregate"
    if o["paper"] in CROSS: return "excluded: cross-table"
    return "primary" if o["smote_kind"] == RC.PLAIN else "wrapper"
# ---- ค่าซ้ำข้าม paper: ทุกคู่ paper, ชื่อ normalise เดียวกัน, ค่า smote/proposed/best_other เท่ากันเป็นสตริง (>=3 หลัก ไม่ใช่ 0 หรือ 1)
by = defaultdict(list)
for i, (o, l) in enumerate(zip(O, LK), 2):
    nm = DR[l["record_id"]]["normalized_name"] if l["record_id"] else norm(o["dataset"])
    by[o["paper"]].append((nm, i, o))
def ok(v): return bool(v) and len(re.sub(r"\D", "", v)) >= 3 and v not in ("0", "1", "0.0", "1.0", "100", "100.00")
ident = []
for a, b in itertools.combinations(sorted(by), 2):
    da = defaultdict(list)
    for nm, i, o in by[a]: da[nm].append((i, o))
    for nm, j, o2 in by[b]:
        for i, o in da.get(nm, []):
            for k1 in ("smote", "proposed", "best_other_value"):
                for k2 in ("smote", "proposed", "best_other_value"):
                    if ok(o[k1]) and o[k1] == o2[k2]:
                        ident.append(dict(paper_a=a, row_a=i, paper_b=b, row_b=j, dataset=nm, field_a=k1, field_b=k2, value=o[k1],
                                          metric_a=o["metric"][:40], metric_b=o2["metric"][:40]))
pairs = defaultdict(lambda: dict(datasets=set(), smote_smote=set()))
for r in ident:
    key = (r["paper_a"], r["paper_b"]); pairs[key]["datasets"].add(r["dataset"])
    if r["field_a"] == r["field_b"] == "smote": pairs[key]["smote_smote"].add(r["dataset"])
flag_pairs = {k: v for k, v in pairs.items() if len(v["datasets"]) >= 3}
with open("out/baseline_identical_values.csv", "w", encoding="utf-8", newline="") as fh:
    rows = [r for r in ident if (r["paper_a"], r["paper_b"]) in flag_pairs]
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
ident_with = defaultdict(list)
for (a, b), v in flag_pairs.items():
    note = f"{len(v['smote_smote'])} SMOTE values identical on {len(v['datasets'])} shared data sets"
    ident_with[a].append(f"{b} ({note})"); ident_with[b].append(f"{a} ({note})")
# ---- EMDO Table 5 (MAUC) เทียบกับตาราง MAUC ของ AMDO ทุกคอลัมน์ (ค่าที่ extraction ไม่ได้เก็บ) จาก layout text ของ PDF
def _layout(pk, page):
    return subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), PM[pk]["main"], "-"], capture_output=True, text=True).stdout
def _rows(seg):
    out = {}
    for ln in seg.splitlines():
        m = re.match(r"\s*([A-Za-z][A-Za-z\-]+)\s+(.*)", ln)
        if m and re.search(r"\d", m.group(2)): out[m.group(1).lower()] = re.findall(r"\d+\.\d{2}", m.group(2))
    return out
_a = _layout("AMDO", 10); _a = _rows(_a[_a.find("Means and Standard Deviations of AUCm"):][:2600])
_e = _layout("EMDO", 15); _e = _rows(_e[_e.find("Table 5"):][:2200])
_cols = ["Base", "SSMOTE", "GCS", "ABNC", "OSMOTE"]
_shared = [k for k in _e if k in _a and len(_a[k]) >= 12 and len(_e[k]) >= 18]
_same = {c: sum(_a[k][-12:][2*i:2*i+2] == _e[k][2*i:2*i+2] for k in _shared) for i, c in enumerate(_cols)}
_same["AMDO"] = sum(_a[k][-2:] == _e[k][14:16] for k in _shared)
EMDO_CHECK = f"EMDO Table 5 (MAUC, p.15) vs AMDO MAUC table (p.10), {len(_shared)} shared data sets; identical mean and SD per column: " + ", ".join(f"{c} {n}/{len(_shared)}" for c, n in _same.items())
ident_with["EMDO"] = [EMDO_CHECK]; ident_with["AMDO"] = [EMDO_CHECK]
if not all(n == len(_shared) == 9 for n in _same.values()): print("NOTE: EMDO/AMDO column check not all identical:", EMDO_CHECK)
# ---- ตาราง paper
rows = []
for k in sorted(k for k, j in F.items() if (j.get("outcome") or {}).get("smote_in_baselines") == "yes"):
    oc = (F[k].get("outcome") or {})
    po = Counter(part(o) for o in O if o["paper"] == k)
    sets = "; ".join(f"{p} {n}" for p, n in sorted(po.items())) or "no per-dataset pair extracted"
    if k in IMPORTED:
        q, wf, src, de, pe = IMPORTED[k]; prov, ev = "B3 published scores imported (stated)", f'"{q}" ({find(k, q, wf)})'
        deq, peq = de, pe
    elif k in ident_with and k not in EARLIER_SOURCE:
        prov = "B4 identical to another corpus paper's published values; re-run or reuse not stated"
        ev = "; ".join(ident_with[k]) + " (out/baseline_identical_values.csv)"
        if k in SAME_DATA_STATED:
            q, wf = SAME_DATA_STATED[k]; deq = f'stated same data sets as the source: "{q}" ({find(k, q, wf)})'
        else: deq = "not stated"
        peq = "not stated whether folds/protocol match the source" + (f'; SMOTE configuration given: "{CONFIG[k][0]}" ({find(k, *CONFIG[k])})' if k in CONFIG else "")
    elif k in CONFIG:
        q, wf = CONFIG[k]; prov, ev = "B1 same study, SMOTE implementation/configuration described", f'"{q}" ({find(k, q, wf)})'
        deq, peq = "same data entry in the same results table", "single protocol described for all methods in the table"
    else:
        prov, ev = "B2 same study presumed; how SMOTE was run not found", "keyword search found no implementation/configuration statement for SMOTE"
        deq, peq = "same data entry in the same results table", "single protocol described; SMOTE settings not reported"
    idn = "; ".join(ident_with.get(k, [])) + (f" -- {EARLIER_SOURCE[k]}" if k in EARLIER_SOURCE else "")
    rows.append(dict(paper=k, year=F[k].get("year", ""), smote_kind=(oc.get("smote_name_as_printed") or "")[:80], granularity=oc.get("results_granularity", ""),
                     comparison_rows=sets, provenance=prov, provenance_evidence=ev, dataset_equivalence=deq, protocol_equivalence=peq, identical_values_with=idn))
yr = {r["paper_key"]: r["year"] for r in DR.values()}
for r in rows: r["year"] = yr.get(r["paper"], "")
with open("out/baseline_provenance_papers.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
# ---- ระดับแถว (score pair) ใน primary และ wrapper
P = {r["paper"]: r["provenance"][:2] for r in rows}
pr = defaultdict(Counter)
for o, l in zip(O, LK):
    p = part(o)
    if p in ("primary", "wrapper"):
        prov = P.get(o["paper"], "?")
        cat = DR[l["record_id"]]["category"] if l["record_id"] else "unlinked"
        pr[p][(prov, "linked" if l["record_id"] else "unlinked")] += 1
        pr[p + "_cat"][(prov, cat)] += 1
S = dict(unit_papers="papers whose extraction lists SMOTE among the baselines (ai-draft/full smote_in_baselines = yes)", papers=len(rows),
         provenance_papers=dict(Counter(r["provenance"][:2] for r in rows)),
         provenance_papers_with_per_dataset_rows=dict(Counter(r["provenance"][:2] for r in rows if ("primary" in r["comparison_rows"] or "wrapper" in r["comparison_rows"]))),
         identical_value_pairs={f"{a} | {b}": dict(shared_datasets_with_identical_values=len(v["datasets"]), identical_smote_values=len(v["smote_smote"])) for (a, b), v in flag_pairs.items()},
         rows_by_partition_and_provenance={p: {f"{a}|{b}": n for (a, b), n in c.items()} for p, c in pr.items()})
json.dump(S, open("out/baseline_provenance_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
