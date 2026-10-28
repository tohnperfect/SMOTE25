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
LAB = {"original": "Original", "repository-defined": "Repository-defined", "modified": "Modified", "synthetic": "Synthetic",
       "not stated": "Cannot be told", "unmatched": "Result row not matched to a dataset"}
for k, lab in LAB.items():
    v = bt[k]; row = f'{lab} & {v["rows"]} & {v["papers"]} & {v["proposed_higher"]} & {v["smote_higher"]} & {v["equal"]}\\\\'
    ck(f"tex wins table row '{lab}'", row in tex, row)
allrow = f'All & {pr["rows"]} & {pr["papers"]} & {pr["proposed_higher"]} & {pr["smote_higher"]} & {pr["equal"]}\\\\'
ck("tex wins table row 'All'", allrow in tex, allrow)
ck("tex standard rows sentence", f'on these {std["rows"]} standard rows SMOTE wins in {std["smote_higher"]} and ties in {std["equal"]}' in tex)
ck("tex primary rows/wins/ties/losses sentence (521/402/39/80 since R8)", f'{pr["rows"]} comparisons' in tex and f'wins in {pr["proposed_higher"]} rows, ties in {pr["equal"]} and loses in {pr["smote_higher"]}' in tex)
ck("tex wrapper 207 and RBBoost 86/63", f'contribute {P["wrapper_eligible"]["rows"]} rows' in tex and "Its 86 rows, 63 of them on repository-defined" in tex)
ov = open("manuscript/overview.json", encoding="utf-8").read()
ck("overview.json standard rows", f'บนชุดมาตรฐาน {std["rows"]} แถว SMOTE ชนะ {std["smote_higher"]} เสมอ {std["equal"]}' in ov)
ck("overview.json primary rows/wins/ties/losses", f'{pr["rows"]} แถว: วิธีที่เสนอชนะ {pr["proposed_higher"]} เสมอ {pr["equal"]} แพ้ {pr["smote_higher"]}' in ov)
pdf = "manuscript/data-section-draft-preview.pdf"
pt = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
ck("preview PDF newer than tex and shows current standard count", os.path.getmtime(pdf) >= os.path.getmtime("manuscript/data-section-draft.tex") and f'{std["rows"]} standard rows' in re.sub(r"\s+", " ", pt))
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
ck("Atlas manuscript tab shows current standard count", f'{std["rows"]} standard rows' in X["manuscript"]["html"])
ck("Atlas reconciled_with sha = current outcomes", el["reconciled_with"]["outcomes_sha256"] == sha("out/verified_outcomes.csv"))
# 6 handoff
H = open("handoff.md", encoding="utf-8").read()
ck("handoff records current standard count and audit file", f"{std['rows']}" in H and "outcome_mapping_audit.csv" in H)
# R8 (29 Oct 2026): papers excluded for an unconfirmed SMOTE comparator are the same in the rule-A set and the all-metric set
_WA = json.load(open("out/winloss_allmetric_summary.json", encoding="utf-8"))
_r8 = set(RC["partitions"]["excluded"]["comparator"]["reasons"])
ck("R8 excluded papers: rule-A set = all-metric set", _r8 == set(_WA["excluded"]) and _r8, f"{sorted(_r8)} vs {sorted(_WA['excluded'])}")
w = max(len(n) for n, _, _ in res)
for n, ok, d in res: print(f"{'ok  ' if ok else 'FAIL'} {n:{w}s} {d}")
print(f"{sum(ok for _, ok, _ in res)}/{len(res)} ok"); sys.exit(0 if all(ok for _, ok, _ in res) else 1)
