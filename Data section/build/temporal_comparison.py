"""temporal_comparison.py  Analysis D (19 ต.ค. 2026): เทียบ paper รุ่นแรกกับรุ่นหลัง

ช่วงเวลา: 1972-2009 / 2010-2019 / 2020-2026 (ช่วงเดิมของ out/data_handling_summary.json และ Atlas; ช่วงแรกคือยุคก่อน KEEL imbalanced
benchmark แพร่หลาย และทำให้แต่ละช่วงมี paper พอ ๆ กันในสองช่วงหลัง) ปีจาก out/dataset_records.csv
อ่าน   out/dataset_records.csv, out/modified_operations_audit.csv, out/baseline_provenance_papers.csv, out/verified_outcomes.csv,
       out/outcome_dataset_links.csv, out/data_handling_matrix.csv (crit_type เป็น ai_draft ยังไม่ตรวจ -> รายงานแยกพร้อมธง)
เขียน  out/temporal_comparison.json
ทุกตัวชี้วัดรายงาน count + ตัวหาร; หน่วยระบุในชื่อ key
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE); sys.path.insert(0, "build")
import reconcile_counts as RC
PER = [("1972-2009", 0, 2009), ("2010-2019", 2010, 2019), ("2020-2026", 2020, 2100)]
def per(y): return next(n for n, a, b in PER if a <= int(y) <= b)
R = [r for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig")) if r["is_placeholder"] == "no"]
yr = {r["paper_key"]: r["year"] for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig"))}
CATS = ["original", "repository-defined", "modified", "synthetic", "not stated"]
def frac(a, b): return dict(n=a, of=b, pct=round(100 * a / b, 1) if b else None)
out = {}
miss = lambda v: (not (v or "").strip()) or v.strip().lower().startswith("not stated in paper") or v.strip().lower() in ("none", "null")
# reuse: names used by >=5 papers corpus-wide
byname = defaultdict(set)
for r in R: byname[r["normalized_name"]].add(r["paper_key"])
MOD = list(csv.DictReader(open("out/modified_operations_audit.csv", encoding="utf-8")))
BP = list(csv.DictReader(open("out/baseline_provenance_papers.csv", encoding="utf-8")))
O = list(csv.DictReader(open("out/verified_outcomes.csv", encoding="utf-8-sig"))); LK = list(csv.DictReader(open("out/outcome_dataset_links.csv", encoding="utf-8")))
CROSS = {k for k, v in RC.CROSS_TABLE_REVIEW.items() if v.startswith("cross-table")}
DH = {r["key"]: r for r in csv.DictReader(open("out/data_handling_matrix.csv", encoding="utf-8-sig"))}
for name, a, b in PER:
    E = [r for r in R if per(r["year"]) == name]; P = sorted({r["paper_key"] for r in E}); nE, nP = len(E), len(P)
    d = dict(papers_with_named_entries=nP, entries=nE)
    d["category_entries"] = {c: frac(sum(r["category"] == c for r in E), nE) for c in CATS}
    d["category_papers_with_any"] = {c: frac(len({r["paper_key"] for r in E if r["category"] == c}), nP) for c in CATS}
    d["papers_only_original_or_repository"] = frac(sum(all(r["category"] in ("original", "repository-defined") for r in E if r["paper_key"] == p) for p in P), nP)
    M = [m for m in MOD if per(m["year"]) == name]; mP = {m["paper_key"] for m in M}
    d["modified_entries"] = len(M); d["modified_papers"] = len(mP)
    d["modification_ops_entries_of_modified"] = {o: frac(sum(o in m["ops"].split(";") for m in M), len(M)) for o in ["CS", "US", "IM", "SF", "FM", "NI", "LC"]}
    d["modification_ops_papers_of_all_papers"] = {o: frac(len({m["paper_key"] for m in M if o in m["ops"].split(";")}), nP) for o in ["CS", "US", "IM", "SF", "FM", "NI", "LC"]}
    d["modifying_papers_with_stated_purpose"] = frac(len({m["paper_key"] for m in M if not m["purpose_stated_by_authors"].startswith("none")}), len(mP))
    d["reporting_entries"] = {f: frac(sum(not miss(r[f]) for r in E), nE) for f in ["n_instances", "n_features", "n_classes", "n_minority", "ir_as_printed", "source_as_reported"]}
    d["papers_stating_ir_definition"] = frac(sum(not miss(next(r["ir_definition_paper"] for r in E if r["paper_key"] == p)) for p in P), nP)
    d["uses_on_names_shared_by_5plus_papers"] = frac(len({(r["paper_key"], r["normalized_name"]) for r in E if len(byname[r["normalized_name"]]) >= 5}),
                                                      len({(r["paper_key"], r["normalized_name"]) for r in E}))
    d["uses_on_single_paper_names"] = frac(len({(r["paper_key"], r["normalized_name"]) for r in E if len(byname[r["normalized_name"]]) == 1}),
                                           len({(r["paper_key"], r["normalized_name"]) for r in E}))
    B = [x for x in BP if x["year"] and per(x["year"]) == name]
    d["smote_baseline_papers"] = frac(len(B), nP)
    d["provenance_papers_of_smote_baseline_papers"] = {k: frac(sum(x["provenance"].startswith(k) for x in B), len(B)) for k in ["B1", "B2", "B3", "B4"]}
    pr = [(o, l) for o, l in zip(O, LK) if per(yr[o["paper"]]) == name and not RC.AGG_RE.match(o["dataset"] or "") and o["paper"] not in CROSS and o["paper"] not in RC.EXCLUDED_COMPARATOR and o["smote_kind"] == RC.PLAIN]
    d["primary_rows"] = len(pr); d["primary_papers"] = len({o["paper"] for o, _ in pr})
    d["primary_rows_by_category"] = {c: frac(sum(o["how_obtained"] == c for o, _ in pr), len(pr)) for c in CATS + ["unmatched"]}
    d["primary_rows_sign"] = dict(Counter(o["raw_sign"] for o, _ in pr))
    ct = Counter(DH[p]["crit_type"] for p in P if p in DH)
    d["selection_rationale_papers_AI_DRAFT_UNVERIFIED"] = {k: frac(v, sum(ct.values())) for k, v in ct.items()}
    out[name] = d
json.dump(dict(periods=[p[0] for p in PER], note="counts with denominators; crit_type is ai_draft (unverified) and is reported separately", by_period=out),
          open("out/temporal_comparison.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, d in out.items():
    print("==", k, "papers", d["papers_with_named_entries"], "entries", d["entries"])
    print("  cat entries", {c: v["pct"] for c, v in d["category_entries"].items()})
    print("  cat papers", {c: f'{v["n"]}/{v["of"]}' for c, v in d["category_papers_with_any"].items()}, "only orig/repo", d["papers_only_original_or_repository"])
    print("  mod", d["modified_entries"], d["modified_papers"], {o: f'{v["n"]}/{v["of"]}' for o, v in d["modification_ops_papers_of_all_papers"].items()}, "purpose", d["modifying_papers_with_stated_purpose"])
    print("  report", {f: v["pct"] for f, v in d["reporting_entries"].items()}, "IRdef", d["papers_stating_ir_definition"])
    print("  reuse5+", d["uses_on_names_shared_by_5plus_papers"], "single", d["uses_on_single_paper_names"])
    print("  smote papers", d["smote_baseline_papers"], {k: f'{v["n"]}/{v["of"]}' for k, v in d["provenance_papers_of_smote_baseline_papers"].items()})
    print("  primary rows", d["primary_rows"], d["primary_papers"], {c: v["n"] for c, v in d["primary_rows_by_category"].items()}, d["primary_rows_sign"])
    print("  crit (draft)", {c: f'{v["n"]}/{v["of"]}' for c, v in d["selection_rationale_papers_AI_DRAFT_UNVERIFIED"].items()})
