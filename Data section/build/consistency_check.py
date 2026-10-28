"""consistency_check.py  ตรวจว่า manuscript, workbook, Atlas, audit trail และ handoff ใช้ข้อมูลชุดเดียวกัน (อ่านอย่างเดียว, 19 ต.ค. 2026)
รัน: python3 build/consistency_check.py   (exit 1 ถ้ามีข้อใดไม่ผ่าน)
"""
import csv, hashlib, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
res = []
def ck(name, ok, detail=""): res.append((name, bool(ok), detail))
sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()
rc = lambda f: list(csv.DictReader(open(f, encoding="utf-8-sig")))
RC = json.load(open("out/reconcile_counts.json", encoding="utf-8"))
# 1 แหล่งข้อมูลกับไฟล์ที่สร้างจากมัน
for k, f in [("datasets", "out/verified_datasets.csv"), ("outcomes", "out/verified_outcomes.csv"), ("summary", "out/full_summary.json")]:
    ck(f"reconcile_counts sources.{k} sha = current {f}", RC["sources"][k]["sha256"] == sha(f))
ck("reconcile checks all ok", all(v["ok"] for v in RC["checks"].values()), f'{sum(v["ok"] for v in RC["checks"].values())}/{len(RC["checks"])}')
DRS = json.load(open("out/dataset_records_summary.json", encoding="utf-8"))
ck("dataset_records built from current verified_datasets", DRS["sources"]["datasets"]["sha256"] == sha("out/verified_datasets.csv"))
DF = json.load(open("out/difficulty_evidence.json", encoding="utf-8"))
ck("difficulty_evidence sources current", all(sha(f) == h for f, h in DF["sources"].items()))
O = rc("out/verified_outcomes.csv"); LK = rc("out/outcome_dataset_links.csv")
ck("outcome links align row-by-row with verified_outcomes", len(LK) == len(O) and all(a["paper"] == b["paper"] and a["dataset"] == b["dataset"] for a, b in zip(LK, O)))
ck("no unaudited name differences left", not [l for l in LK if l["name_check"] == "differs"], str(sum(l["name_check"] == "differs" for l in LK)))
# 2 audit trail ครอบทุกแถวที่มี mapping_audit
AU = rc("out/outcome_mapping_audit.csv")
audited = {i for i, o in enumerate(O, 2) if o.get("mapping_audit")}
ck("every audited row is in outcome_mapping_audit.csv", audited <= {int(a["outcome_csv_line"]) for a in AU}, f"{len(audited)} rows")
ck("audit corrected values are what the CSV holds now",
   all(O[int(a["outcome_csv_line"]) - 2][a["field"]] == a["corrected_value"] for a in AU))
# 3 manuscript
P = RC["partitions"]; pr = P["primary"]; bt = pr["by_type"]; std = RC["outcomes"]["plain_per_dataset_standard"]
tex = open("manuscript/data-section-draft.tex", encoding="utf-8").read()
# 29 Oct 2026: Wins section uses the all-metric results (Toon's win/loss definition); rule A kept as robustness
WA = json.load(open("out/winloss_allmetric_summary.json", encoding="utf-8"))
texn = re.sub(r"\s+", " ", tex)
HY = json.load(open("out/hypotheses.json", encoding="utf-8"))
fmt = lambda n: f"{n:,}"
pm = WA["plain_smote_only"]["by_metric_group"]
NAME = {"Recall/sensitivity": "Recall (sensitivity)"}
for g, v in pm.items():
    row = f'{NAME.get(g, g)} & {v["papers"]} & {fmt(v["rows"])} & {fmt(v["win"])} & {v["tie"]} & {v["loss"]} & {v["not_comparable"]}\\\\'
    ck(f"tex by-metric row '{g}'", row in tex, row)
o = WA["plain_smote_only"]["overall_all_metrics"]
ck("tex by-metric row 'All metrics'", f'All metrics & {o["papers"]} & {fmt(o["rows"])} & {fmt(o["win"])} & {o["tie"]} & {o["loss"]} & {o["not_comparable"]}\\\\' in tex)
LAB = {"original": "Original", "repository-defined": "Repository-defined", "modified": "Modified", "synthetic": "Synthetic",
       "not stated": "Cannot be told", "unmatched": "Not matched to a dataset"}
bt = HY["all_metric_plain"]["by_type"]
for k, lab in LAB.items():
    v = bt[k]
    row = f'{lab} & ' 
    ok = any(l.startswith(row) and f'& {v["papers"]} & {fmt(v["rows"])} & {fmt(v["win"])} & {v["tie"]} & {v["loss"]} &' in l for l in tex.split("\n"))
    ck(f"tex by-type row '{lab}' (all-metric)", ok, f'{v["papers"]}/{v["rows"]}/{v["win"]}/{v["tie"]}/{v["loss"]}')
ov_ = HY["all_metric_plain"]["overall"]
ck("tex overall wins/ties/losses sentence", f'the proposed method wins {fmt(ov_["win"])}, ties {ov_["tie"]} and loses {ov_["loss"]}' in texn)
ck("tex rule-A robustness sentence", f'gives {pr["rows"]} comparisons, in which the proposed method wins in {pr["proposed_higher"]} rows, ties in {pr["equal"]} and loses in {pr["smote_higher"]}' in texn)
h = HY["all_metric_plain"]["H1_primary_modsyn_vs_original"]
ck("tex H1 GEE and conditional OR", f'{h["M1_gee"]["odds_ratio"]:.2f}' in tex and f'{h["M2_conditional"]["odds_ratio"]:.2f}' in tex)
npt = sum(v["overall_all_metrics"]["rows"] for v in WA["non_plain_by_comparator"].values())
ck("tex non-plain total", f'contribute {npt} comparisons' in texn, npt)
ov = open("manuscript/overview.json", encoding="utf-8").read()
ck("overview.json all-metric totals", f'{fmt(o["rows"])} แถว' in ov and f'ชนะ {fmt(ov_["win"])} เสมอ {ov_["tie"]} แพ้ {ov_["loss"]}' in ov)
ck("overview.json rule-A robustness", f'{pr["rows"]} แถว: วิธีที่เสนอชนะ {pr["proposed_higher"]} เสมอ {pr["equal"]} แพ้ {pr["smote_higher"]}' in ov)
pdf = "manuscript/data-section-draft-preview.pdf"
pt = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
ck("preview PDF newer than tex and shows the all-metric total", os.path.getmtime(pdf) >= os.path.getmtime("manuscript/data-section-draft.tex") and f'{fmt(o["rows"])} comparisons on' in re.sub(r"\s+", " ", pt))
# 4 workbook
try:
    import openpyxl
    wb = openpyxl.load_workbook("SMOTE25_data_extraction.xlsx", read_only=True)
    def sheet_eq(name, rows):
        v = list(wb[name].iter_rows(values_only=True)); cols = list(v[0])
        if cols != list(rows[0]) or len(v) - 1 != len(rows): return False, f"cols/rows {len(cols)}/{len(v)-1}"
        bad = sum(1 for x, r in zip(v[1:], rows) for c, val in zip(cols, x)
                  if (("" if val is None else str(val)).lstrip("'") if str(r[c])[:1] in "=+-@" else ("" if val is None else str(val))) != r[c])
        return bad == 0, f"{bad} differing cells"
    ok, d = sheet_eq("outcomes_verified", O); ck("workbook outcomes_verified = verified_outcomes.csv", ok, d)
    ok, d = sheet_eq("datasets_verified", rc("out/verified_datasets.csv")); ck("workbook datasets_verified = verified_datasets.csv", ok, d)
except Exception as e:
    ck("workbook readable", False, repr(e))
# 5 Atlas
X = json.load(open("out/explorer_data.json", encoding="utf-8"))
html = open("out/dataset-atlas.html", encoding="utf-8").read()
ck("Atlas html embeds current explorer_data.json", json.dumps(X, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") in html)
el = X["outcome"]["eligibility"]
ck("Atlas eligibility = reconcile partitions", (el["plain"]["rows"], el["plain"]["up"], el["plain"]["dn"], el["plain"]["eq"], el["wrapper"]["rows"], el["excluded"]["rows"]) ==
   (pr["rows"], pr["proposed_higher"], pr["smote_higher"], pr["equal"], P["wrapper_eligible"]["rows"], P["excluded"]["rows"]))
ck("Atlas outcome rows = verified_outcomes (dataset, scores, sign, type, mapping)",
   len(X["outcome"]["rows"]) == len(O) and all(all(a[k] == b[k] for k in ("paper", "dataset", "proposed", "smote", "raw_sign", "how_obtained", "n_instances", "mapping_audit")) for a, b in zip(X["outcome"]["rows"], O)))
ck("Atlas manuscript tab shows the all-metric total", f'{fmt(o["rows"])} comparisons on' in re.sub(r"\s+", " ", X["manuscript"]["html"]))
ck("Atlas reconciled_with sha = current outcomes", el["reconciled_with"]["outcomes_sha256"] == sha("out/verified_outcomes.csv"))
# 6 handoff
H = open("handoff.md", encoding="utf-8").read()
ck("handoff records the all-metric total and audit file", fmt(o["rows"]) in H and "outcome_mapping_audit.csv" in H)
# R8 (29 Oct 2026): papers excluded for an unconfirmed SMOTE comparator are the same in the rule-A set and the all-metric set
_WA = json.load(open("out/winloss_allmetric_summary.json", encoding="utf-8"))
_r8 = set(RC["partitions"]["excluded"]["comparator"]["reasons"])
ck("R8 excluded paper is excluded in the all-metric set too", _r8 and _r8 <= set(_WA["excluded"]), f"{sorted(_r8)} vs {sorted(_WA['excluded'])}")
_cls = {k.split(" /")[0]: v["comparator_group"] for k, v in _WA["per_paper"].items()}
_ra = {"primary": set(), "wrapper": set()}
for _p in RC["partitions"]["wrapper_eligible"]["papers_list"]: _ra["wrapper"].add(_p.split(" /")[0])
_bad = [k for k in _ra["wrapper"] if _cls.get(k) in ("plain SMOTE", None)]
ck("paper classes: every rule-A wrapper paper is non-plain in the all-metric set", not _bad, _bad)
w = max(len(n) for n, _, _ in res)
for n, ok, d in res: print(f"{'ok  ' if ok else 'FAIL'} {n:{w}s} {d}")
print(f"{sum(ok for _, ok, _ in res)}/{len(res)} ok"); sys.exit(0 if all(ok for _, ok, _ in res) else 1)
