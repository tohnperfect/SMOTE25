"""สร้างหน้า SMOTE25 Dataset Atlas (HTML ไฟล์เดียว) จากข้อมูลใน Data section/

ฉบับ 18 ต.ค. 2026 ใช้ผลอ่าน PDF ครบ 72 paper (ai-draft/full/ ผ่าน build/full_extraction.py) เป็นข้อมูลหลัก
อ่าน  SMOTE25_data_extraction.xlsx (ชีต papers: ปี venue task), out/data_handling_matrix.csv (รหัส 4 มิติ),
      out/data_handling_summary.json, out/dataset_usage_draft.json, ai-draft/dataset_variants.json,
      out/full_datasets.csv, out/full_outcome_rows.csv, out/full_summary.json, out/section7_key_map.csv
เขียน out/explorer_data.json และ out/dataset-atlas.html

19 ต.ค. 2026 (Toon อนุมัติ): ใช้กติกาเดียวกับ manuscript โดย import จาก build/reconcile_counts.py
  - ชื่อ dataset ไม่นับ placeholder ที่เป็นคำบรรยาย (R1, PLACEHOLDER_RE)
  - ผลเทียบแต่ละแถวมีช่อง eligible / excluded_reason: แถวค่ารวมหลายชุด (R4, AGG_RE) และคู่ค่าข้ามตาราง
    ที่ตรวจแล้ว (R6, CROSS_TABLE_REVIEW) ไม่เข้าชุดเทียบ แต่ยังอยู่ในหน้าเพื่อ audit
  - plain SMOTE กับ SMOTE แบบห่อแสดงแยกกันเสมอ (R5)
  - ตรวจตัวเลขกับ out/reconcile_counts.json (partitions) ก่อนเขียน ถ้าไม่ตรงหรือ CSV เปลี่ยนจะหยุด
  - แท็บสำรวจ dataset อ่าน out/dataset_records.csv และ _summary.json (รัน build/dataset_records.py ก่อน) ตรวจ sha256 และตัวนับก่อนใช้
รันจาก Data section/ หลัง build/data_handling_matrix.py, build/full_extraction.py, build/section7_key_map.py และ build/reconcile_counts.py:
    python3 build/make_atlas.py
หน้าที่ publish เป็น Artifact คือ out/dataset-atlas.html (ไม่มี <html>/<body> เพราะ Artifact ใส่ให้ตอน publish)
"""
import collections as C, csv, json, os, re, sys
import openpyxl

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "build"))
import analyse_dataset_usage as A  # norm() และ provenance() ตัวเดียวกับการนับ dataset
import reconcile_counts as RC      # กติกา R1 R4 R5 R6 ตัวเดียวกับ manuscript

def p(*a): return os.path.join(HERE, *a)
def rcsv(path): return list(csv.DictReader(open(p(path), encoding="utf-8-sig")))

wb = openpyxl.load_workbook(p("SMOTE25_data_extraction.xlsx"), read_only=True)
pr = list(wb["papers"].iter_rows(values_only=True)); ph = pr[0]
meta = {r[1]: dict(zip(ph, r)) for r in pr[1:]}           # key = method_name
M = {r["key"]: r for r in rcsv("out/data_handling_matrix.csv")}
K7 = {r["data_section_key"]: r for r in rcsv("out/section7_key_map.csv")}  # จาก build/section7_key_map.py
V = {v["name"]: v for v in json.load(open(p("ai-draft/dataset_variants.json"), encoding="utf-8"))}
FD = rcsv("out/verified_datasets.csv")   # 18 ต.ค. รอบตรวจครบ: ใช้ไฟล์ที่ผ่านการตรวจกับ PDF แล้ว (มีคอลัมน์ value_status)
FO = rcsv("out/verified_outcomes.csv")
FS = json.load(open(p("out/full_summary.json"), encoding="utf-8"))
FP = {x["key"]: x for x in FS["papers"]}

# ---- datasets tab: group by normalised name ----
ds = C.defaultdict(lambda: {"printed": set(), "papers": set(), "N": set(), "how": C.Counter()})
for r in FD:
    nm = r["name"] or ""
    if not nm or RC.PLACEHOLDER_RE.match(nm): continue   # R1: คำบรรยายแทนชื่อ ไม่นับเป็นชื่อ dataset
    d = ds[A.norm(nm)]; d["printed"].add(nm); d["papers"].add(r["paper"]); d["how"][r["how_obtained_final"]] += 1
    if r["n_instances"] not in ("", "None", None): d["N"].add(r["n_instances"])
out_ds = []
for k, d in ds.items():
    v = V.get(k)
    out_ds.append([k, sorted(d["printed"]), sorted(d["papers"]), A.provenance(k), sorted(d["N"], key=lambda s: (len(s), s)),
                   v["sev"] if v else "", [f["msg"] for f in v["flags"]] if v else [], dict(d["how"])])
out_ds.sort(key=lambda x: (-len(x[2]), x[0]))

# ---- papers tab ----
byp = C.defaultdict(list)
for r in FD:
    byp[r["paper"]].append([r["name"], r["group"], r["source_repo"], r["n_instances"], r["n_features"], r["n_classes"],
                            r["n_minority"], r["n_majority"], r["ir_printed"], r["how_obtained_final"], r["how_basis"],
                            r["how_obtained_detail"], r["ref"], r["class_distribution"]])
pp = []
for k, m in meta.items():
    mx = M.get(k, {}); fp = FP.get(k, {})
    pp.append(dict(k=k, y=m["year"], v=m["venue"], t=m["task"], nc=m["n_datasets_claimed"],
                   src=mx.get("sources", ""), org=mx.get("origin", ""), ct=mx.get("crit_type", ""), b=mx.get("basis", ""),
                   inh=mx.get("inherited_from", ""), mr=mx.get("minority_rule", ""), emp=mx.get("empirical", ""),
                   rec=mx.get("record", ""), st=mx.get("src_text", ""), cr=mx.get("crit_text", ""),
                   pt=mx.get("prep_text", ""), q=mx.get("quote", ""), rows=byp.get(k, []),
                   gran=fp.get("results_granularity", ""), ctab=fp.get("characteristics_table", ""), irdef=fp.get("ir_definition", ""),
                   nunc=fp.get("n_uncertain", 0), notes=fp.get("notes", ""),
                   s7=K7.get(k, {}).get("section7_key", ""), bib=K7.get(k, {}).get("bibkey", ""),
                   s7emp=K7.get(k, {}).get("section7_empirical", "")))
pp.sort(key=lambda x: (x["y"], x["k"]))

S = json.load(open(p("out/data_handling_summary.json"), encoding="utf-8"))
U = json.load(open(p("out/dataset_usage_draft.json"), encoding="utf-8"))
keep = ["paper", "dataset", "how_obtained", "how_basis", "how_obtained_detail", "n_instances", "n_features", "n_classes", "ir_printed",
        "metric", "classifier", "table", "page", "smote_name", "smote_kind", "proposed", "smote", "diff", "raw_sign",
        "best_other", "best_other_value", "match", "eligible", "excluded_reason"]
CROSS = {k for k, v in RC.CROSS_TABLE_REVIEW.items() if v.startswith("cross-table")}
for r in FO:
    if RC.AGG_RE.match(r["dataset"] or ""):
        r["eligible"], r["excluded_reason"] = False, "aggregate over datasets, not a per-dataset pair (rule R4)"
    elif r["paper"] in CROSS:
        r["eligible"], r["excluded_reason"] = False, "cross-table pair: " + RC.CROSS_TABLE_REVIEW[r["paper"]] + " (rule R6)"
    elif r["paper"] in RC.EXCLUDED_COMPARATOR:
        r["eligible"], r["excluded_reason"] = False, RC.EXCLUDED_COMPARATOR[r["paper"]] + " (rule R8)"
    else:
        r["eligible"], r["excluded_reason"] = True, ""
def _tal(L): return dict(rows=len(L), papers=len({r["paper"] for r in L}), up=sum(r["raw_sign"] == "+" for r in L),
                         dn=sum(r["raw_sign"] == "-" for r in L), eq=sum(r["raw_sign"] == "=" for r in L))
ELIG = dict(plain=_tal([r for r in FO if r["eligible"] and r["smote_kind"] == RC.PLAIN]),
            wrapper=_tal([r for r in FO if r["eligible"] and r["smote_kind"] == RC.WRAP]),
            excluded=_tal([r for r in FO if not r["eligible"]]), all_rows=len(FO))
# ตรวจกับผลของ build/reconcile_counts.py (R7) ถ้าไม่ตรงให้หยุด ไม่สร้างหน้าที่ตัวเลขขัดกับ manuscript (เพิ่ม 19 ต.ค. รอบ final)
_RCJ = json.load(open(p("out/reconcile_counts.json"), encoding="utf-8"))
_PT = _RCJ.get("partitions")
if not _PT:
    sys.exit("STOP: out/reconcile_counts.json has no 'partitions'; run python3 build/reconcile_counts.py first")
_want = dict(plain=(_PT["primary"]["rows"], _PT["primary"]["papers"], _PT["primary"]["proposed_higher"], _PT["primary"]["smote_higher"], _PT["primary"]["equal"]),
             wrapper=(_PT["wrapper_eligible"]["rows"], _PT["wrapper_eligible"]["papers"], _PT["wrapper_eligible"]["proposed_higher"],
                      _PT["wrapper_eligible"]["smote_higher"], _PT["wrapper_eligible"]["equal"]))
_have = {k: (ELIG[k]["rows"], ELIG[k]["papers"], ELIG[k]["up"], ELIG[k]["dn"], ELIG[k]["eq"]) for k in ("plain", "wrapper")}
if _have != _want or ELIG["excluded"]["rows"] != _PT["excluded"]["rows"]:
    sys.exit(f"STOP: Atlas eligibility {_have} / excluded {ELIG['excluded']['rows']} differs from reconcile_counts.json {_want} / {_PT['excluded']['rows']}")
if not RC.sha_ok(RC.SRC["outcomes"], _RCJ["sources"]["outcomes"]["sha256"]):
    sys.exit("STOP: verified_outcomes.csv changed since reconcile_counts.json was written; rerun build/reconcile_counts.py")
ELIG["reconciled_with"] = {"file": "out/reconcile_counts.json", "outcomes_sha256": _RCJ["sources"]["outcomes"]["sha256"],
                           "checks_ok": sum(v["ok"] for v in _RCJ["checks"].values()), "checks_total": len(_RCJ["checks"])}
# ---- dashboard aggregates (เพิ่ม 19 ต.ค. 2026 รอบ redesign) ----
# ทุกค่าคำนวณจากไฟล์ verified ตัวเดียวกับแท็บอื่น ไม่มีตัวเลขเขียนตายในแม่แบบ
CATS = ["original", "repository-defined", "modified", "synthetic", "not stated"]
_cat = C.Counter(r["how_obtained_final"] for r in FD)
if set(_cat) - set(CATS):
    sys.exit(f"STOP: unexpected dataset categories {set(_cat) - set(CATS)}")
_prov = {}
for repo in ("KEEL", "UCI"):   # เฉพาะ entry ที่ source_repo ตรงตัว ไม่รวมแถวที่ paper บอกแค่ "UCI หรือ KEEL" ระดับกลุ่ม
    sub = [r for r in FD if r["source_repo"] == repo]
    _prov[repo] = dict(total=len(sub), by_cat={c: sum(r["how_obtained_final"] == c for r in sub) for c in CATS})
_mixed = sum(1 for r in FD if r["source_repo"] not in ("KEEL", "UCI") and ("UCI" in r["source_repo"] or "KEEL" in r["source_repo"]))
_sz = C.defaultdict(lambda: C.defaultdict(set))   # ชื่อ -> paper -> ขนาดที่พิมพ์ (R1 ตัด placeholder)
for r in FD:
    if RC.PLACEHOLDER_RE.match(r["name"] or "") or r["n_instances"] in ("", "None", None): continue
    _sz[A.norm(r["name"])][r["paper"]].add(str(r["n_instances"]).strip())
_two = sorted(k for k, v in _sz.items() if len(v) >= 2)
_diff = [k for k in _two if len(set().union(*_sz[k].values())) > 1]
_ex = []
for k in sorted(_diff, key=lambda k: (-len(_sz[k]), k))[:12]:
    sizes = sorted(set().union(*_sz[k].values()), key=lambda x: float(x.replace(",", "")) if x.replace(",", "").replace(".", "").isdigit() else 0)
    _ex.append(dict(name=k, papers=len(_sz[k]), sizes=sizes))
if (len(_two), len(_diff)) != (_RCJ["size_variation"]["names"]["with_size_in_2plus_papers"], _RCJ["size_variation"]["names"]["with_more_than_one_size"]):
    sys.exit("STOP: name-level size variation differs from reconcile_counts.json")
_xc = [r for r in FO if not r["eligible"]]
_typ = lambda L: {t: _tal([r for r in L if r["how_obtained"] == t]) for t in CATS + ["unmatched"] if any(r["how_obtained"] == t for r in L)}
DASH = dict(
    corpus=dict(papers_total=S["papers_total"], papers_empirical=S["papers_empirical"], non_empirical=S["non_empirical"]),
    entries=dict(total=len(FD), by_cat={c: _cat.get(c, 0) for c in CATS},
                 named=sum(1 for r in FD if (r["name"] or "") and not RC.PLACEHOLDER_RE.match(r["name"]))),
    names=dict(distinct=len(out_ds), single_paper=sum(1 for x in out_ds if len(x[2]) == 1),
               datasets_t1=_RCJ["names"]["datasets_t1"], single_paper_datasets_t1=_RCJ["names"]["single_paper_datasets_t1"], families_t1=_RCJ["names"]["families_t1"],
               families={f: dict(exact=v["exact_name_papers"], family=v["family_papers"])
                         for f, v in _RCJ["name_frequencies"].items() if isinstance(v, dict)}),
    provenance=dict(repos=_prov, mixed_group_level=_mixed),
    size_variation=dict(names_with_size_in_2plus_papers=len(_two), names_with_more_than_one_size=len(_diff), examples=_ex,
                        datasets_with_size_in_2plus_papers=_RCJ["size_variation"]["datasets_t1"]["with_size_in_2plus_papers"],
                        datasets_with_more_than_one_size=_RCJ["size_variation"]["datasets_t1"]["with_more_than_one_size"]),
    granularity=dict(C.Counter(x["results_granularity"] for x in FS["papers"])), granularity_papers=len(FS["papers"]),
    baseline=dict(C.Counter(x["smote_kind"] for x in FS["papers"])),
    by_type=dict(plain=_typ([r for r in FO if r["eligible"] and r["smote_kind"] == RC.PLAIN]),
                 wrapper=_typ([r for r in FO if r["eligible"] and r["smote_kind"] == RC.WRAP]), excluded=_typ(_xc)),
    excluded_groups=[dict(paper=k, reason=("aggregate" if all(r["excluded_reason"].startswith("aggregate") for r in _xc if r["paper"] == k)
                                            else "comparator" if k in RC.EXCLUDED_COMPARATOR else "cross-table"),
                          **_tal([r for r in _xc if r["paper"] == k])) for k in sorted({r["paper"] for r in _xc})],
)
# ---- Dataset Explorer (19 ต.ค. 2026): ระเบียนราย entry จาก build/dataset_records.py เฉพาะด้าน dataset ไม่มีผลเทียบ ----
_DRS = json.load(open(p("out/dataset_records_summary.json"), encoding="utf-8"))
if not all(v["ok"] for v in _DRS["checks"].values()):
    sys.exit("STOP: dataset_records_summary.json has failing checks; run python3 build/dataset_records.py")
if not RC.sha_ok(RC.SRC["datasets"], _DRS["sources"]["datasets"]["sha256"]):
    sys.exit("STOP: verified_datasets.csv changed since dataset_records.py ran; rerun it first")
_DR = rcsv("out/dataset_records.csv")
if len(_DR) != DASH["entries"]["total"] or _DRS["counts"]["normalized_names"] != DASH["names"]["distinct"] \
        or any(_DRS["counts"][c] != DASH["entries"]["by_cat"][c] for c in CATS):
    sys.exit("STOP: dataset_records counts differ from the Atlas dataset counts")
DXF = ["record_id", "paper_key", "name_as_reported", "normalized_name", "is_placeholder", "group_in_paper", "source_as_reported",
       "n_instances", "n_features", "n_classes", "n_minority", "n_majority", "class_distribution", "ir_as_printed",
       "category", "category_basis", "preprocessing_note", "evidence_ref", "source_csv_line"]
_dxp = {}
for r in _DR:
    _dxp.setdefault(r["paper_key"], dict(id=r["paper_id"], bib=r["bibkey"], title=r["paper_title"], year=r["year"],
                                         irdef=r["ir_definition_paper"], ctab=r["characteristics_table_paper"]))
DX = dict(fields=DXF, rows=[[r[f] for f in DXF] for r in _DR], papers=_dxp,
          completeness=_DRS["completeness"], conflicts=_DRS["names_with_2plus_papers_and_differing_values"],
          ir_papers=_DRS["papers_ir_definition"], counts=_DRS["counts"], not_available=_DRS["fields_not_available"],
          source_sha256=_DRS["sources"]["datasets"]["sha256"])
# ---- View A/B/C หลักฐาน (เพิ่ม 19 ต.ค. 2026 รอบ evidence-based visualizations) ----
# B: แถว outcome ผูกกับ record_id ด้วย build/outcome_links.py (ลำดับแถวต้องตรงกับ verified_outcomes.csv)
_LK = rcsv("out/outcome_dataset_links.csv")
if len(_LK) != len(FO) or any(a["paper"] != b["paper"] or a["dataset"] != b["dataset"] for a, b in zip(_LK, FO)):
    sys.exit("STOP: out/outcome_dataset_links.csv does not match verified_outcomes.csv row by row; rerun python3 build/outcome_links.py")
_RID = {r["record_id"] for r in _DR}
if any(l["record_id"] and l["record_id"] not in _RID for l in _LK):
    sys.exit("STOP: outcome_dataset_links.csv names a record_id that is not in dataset_records.csv; rerun build/outcome_links.py")
for r, l in zip(FO, _LK):
    r["record_id"], r["link_method"], r["name_check"] = l["record_id"], l["link_method"], l["name_check"]
keep += ["record_id", "link_method", "name_check", "dataset_as_printed", "dataset_table_name", "mapping_audit"]
for r in FO:
    for _c in ("dataset_as_printed", "dataset_table_name", "mapping_audit"): r.setdefault(_c, "")
# A: ผลตรวจรายการ not stated (build/not_stated_audit.py) ไม่แก้ category เดิม
_NSA = rcsv("out/not_stated_audit.csv")
_ns_ids = {r["record_id"] for r in _DR if r["category"] == "not stated"}
if len(_NSA) != DASH["entries"]["by_cat"]["not stated"] or {r["record_id"] for r in _NSA} != _ns_ids:
    sys.exit("STOP: not_stated_audit.csv does not cover exactly the not-stated records; rerun python3 build/not_stated_audit.py")
DX["nsa"] = {r["record_id"]: [r["assessment"], r["assessment_basis"], r["categories_of_matches"], r["matching_records"], r["other_records_same_name"]] for r in _NSA}
# C: หลักฐานความยาก (build/difficulty_evidence.py ตรวจ quote กับ PDF แล้ว)
_DF = json.load(open(p("out/difficulty_evidence.json"), encoding="utf-8"))
for _f, _h in _DF["sources"].items():
    if not RC.sha_ok(p(_f), _h):
        sys.exit(f"STOP: {_f} changed since difficulty_evidence.py ran; rerun python3 build/difficulty_evidence.py")
if any(x not in _RID for it in _DF["items"] for x in it["record_ids"]):
    sys.exit("STOP: difficulty_evidence.json names a record_id that is not in dataset_records.csv")
data = dict(datasets=out_ds, papers=pp, summary=S, dash=DASH, dx=DX,
            usage=dict(listed_total=len(FD), covered_by_aggregate=U["covered_by_aggregate"], aggregate_entry_count=U["aggregate_entry_count"]),
            outcome=dict(papers=FS["papers"], rows=[{k2: r[k2] for k2 in keep} for r in FO], eligibility=ELIG))
data["diff"] = {k: _DF[k] for k in ("types", "confidence", "summary", "items", "papers")}
# ---- แท็บ "Analyses A-F" (เพิ่ม 19 ต.ค. 2026 หลังรอบ A-F) ----
# อ่านผลจากไฟล์ที่ build/*.py ของแต่ละ analysis เขียนไว้ ไม่พิมพ์ตัวเลขใหม่ในแม่แบบ; หยุดถ้าผลไม่ตรงกับข้อมูลที่ตรวจแล้ว
def _md_bullets(path, heading):
    out, on = [], False
    for ln in open(p(path), encoding="utf-8").read().splitlines():
        if ln.startswith("## ") or ln.startswith("Points that matter"):
            on = ln.startswith("## " + heading) or ln.startswith(heading); continue
        if on and ln.startswith("- "): out.append(ln[2:].strip())
        elif on and out and ln.startswith("  ") and ln.strip(): out[-1] += " " + ln.strip()
    return out
def _md_finding(path, heading, part):
    t = open(p(path), encoding="utf-8").read(); t = t[t.find(heading):]; t = t[:t.find("\n## ", 5)] if "\n## " in t[5:] else t
    m = re.search(r"\*\*" + part + r"\.\*\*(.*?)(\n\*\*|\Z)", t, re.S); return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
def _md_table(path):
    rows = [ln for ln in open(p(path), encoding="utf-8").read().splitlines() if ln.startswith("|")]
    cells = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in rows]
    return cells[0], cells[2:]
_MA = rcsv("out/modified_operations_audit.csv"); _MS = json.load(open(p("out/modified_operations_summary.json"), encoding="utf-8"))
if len(_MA) != DASH["entries"]["by_cat"]["modified"] or sum(_MS["combinations"].values()) != len(_MA):
    sys.exit("STOP: modified_operations outputs do not match the modified entries; rerun python3 build/modified_operations.py")
_BPp = rcsv("out/baseline_provenance_papers.csv"); _BPs = json.load(open(p("out/baseline_provenance_summary.json"), encoding="utf-8"))
_BPi = rcsv("out/baseline_identical_values.csv")
if sum(_BPs["rows_by_partition_and_provenance"]["primary"].values()) != ELIG["plain"]["rows"] or sum(_BPs["rows_by_partition_and_provenance"]["wrapper"].values()) != ELIG["wrapper"]["rows"]:
    sys.exit("STOP: baseline_provenance rows do not match the primary/wrapper partitions; rerun python3 build/baseline_provenance.py")
_BC = json.load(open(p("out/benchmark_concentration.json"), encoding="utf-8"))
_named = [r for r in _DR if r["is_placeholder"] == "no"]
_uses = {}
for r in _named: _uses.setdefault(r["normalized_name"], set()).add(r["paper_key"])
if _BC["by_name"]["names"] != len(_uses) or _BC["by_name"]["uses"] != sum(len(v) for v in _uses.values()) or _BC["by_name"]["singletons"] != DASH["names"]["single_paper"]:
    sys.exit("STOP: benchmark_concentration.json does not match dataset_records.csv; rerun python3 build/benchmark_concentration.py")
_TC = json.load(open(p("out/temporal_comparison.json"), encoding="utf-8"))
if sum(d["entries"] for d in _TC["by_period"].values()) != len(_named) or sum(d["primary_rows"] for d in _TC["by_period"].values()) != ELIG["plain"]["rows"]:
    sys.exit("STOP: temporal_comparison.json does not add up to the verified totals; rerun python3 build/temporal_comparison.py")
_CC = json.load(open(p("out/characteristics_coverage.json"), encoding="utf-8"))
if _CC["n_instances"]["entries"]["of"] != len(_named):
    sys.exit("STOP: characteristics_coverage.json denominator differs; rerun python3 build/characteristics_coverage.py")
_CE = rcsv("out/claim_evidence_matrix.csv"); _CEs = json.load(open(p("out/claim_evidence_summary.json"), encoding="utf-8"))
if len(_CE) != _CEs["claims"]:
    sys.exit("STOP: claim_evidence_matrix.csv and its summary disagree; rerun python3 build/claim_evidence.py")
_cat_head, _cat_rows = _md_table("analysis/category_decision_table.md")
_MAF = ["record_id", "paper_key", "year", "name_as_reported", "ops", "ops_conditional", "class_op_kind", "changes_class_structure",
        "changes_sample_composition", "changes_feature_space", "changes_imbalance_level", "what_changed", "evidence_ref",
        "purpose_stated_by_authors", "missing_information", "confidence", "classification_note"]
_E_md = open(p("analysis/E_characteristics_coverage.md"), encoding="utf-8").read()
data["an"] = dict(
    A=dict(fields=_MAF, rows=[[r[f] for f in _MAF] for r in _MA], summary=_MS,
           interpretation=_md_bullets("analysis/A_modified_operations.md", "Interpretation"), limits=_md_bullets("analysis/A_modified_operations.md", "Limits")),
    B=dict(papers=_BPp, summary=_BPs, identical=_BPi,
           interpretation=[_md_finding("analysis/manuscript_ready_findings.md", "## F2.", "Interpretation")],
           limits=_md_bullets("analysis/B_baseline_provenance.md", "Limits")),
    C=dict(summary=_BC, names=sorted(([k, len(v)] for k, v in _uses.items()), key=lambda x: (-x[1], x[0])), top=rcsv("out/benchmark_top_names.csv"),
           interpretation=_md_bullets("analysis/C_benchmark_concentration.md", "Answers"), limits=_md_bullets("analysis/C_benchmark_concentration.md", "Limits")),
    D=dict(data=_TC, interpretation=_md_bullets("analysis/D_temporal_comparison.md", "Observations"), limits=_md_bullets("analysis/D_temporal_comparison.md", "Limits")),
    E=dict(data=_CC, interpretation=_md_bullets("analysis/E_characteristics_coverage.md", "Conclusion"),
           followup=[re.sub(r"\s+", " ", re.sub(r"^\d\.\s*", "", x)).strip() for x in re.split(r"\n(?=\d\. )", _E_md.split("## Recommended")[-1]) if re.match(r"\d\. ", x)]),
    F=dict(rows=_CE, summary=_CEs, interpretation=_md_bullets("analysis/F_claim_evidence.md", "Points that matter"), limits=_md_bullets("analysis/F_claim_evidence.md", "Limits")),
    G=dict(head=_cat_head, rows=_cat_rows,
           notes=[l[2:] for l in open(p("analysis/category_decision_table.md"), encoding="utf-8").read().split("\nNotes")[-1].splitlines() if l.startswith("- ")]),
    sources=dict(A="analysis/A_modified_operations.md", B="analysis/B_baseline_provenance.md", C="analysis/C_benchmark_concentration.md",
                 D="analysis/D_temporal_comparison.md", E="analysis/E_characteristics_coverage.md", F="analysis/F_claim_evidence.md",
                 G="analysis/category_decision_table.md"))
for _k in ("A", "B", "C", "D", "E", "F"):
    if not data["an"][_k]["interpretation"]: sys.exit(f"STOP: no interpretation text parsed for analysis {_k}")
# แท็บร่าง manuscript (เพิ่ม 18 ต.ค. 23:55 ตามที่ Toon ขอ เพื่อนำเสนออาจารย์)
sys.path.insert(0, p("build")); import tex2html
_tex = open(p("manuscript/data-section-draft.tex"), encoding="utf-8").read()
# แท็บ Landscape (19 ต.ค. 2026): อ่าน out/landscape_families.csv และ out/benchmark_candidates.* จาก build/landscape_candidates.py
_LF = list(csv.DictReader(open(p("out/landscape_families.csv"), encoding="utf-8")))
_LC = list(csv.DictReader(open(p("out/benchmark_candidates.csv"), encoding="utf-8")))
_LS = json.load(open(p("out/benchmark_candidates.json"), encoding="utf-8"))
if len(_LF) != _BC["by_name"]["names"] or len({r["family"] for r in _LF}) != _BC["by_family"]["names"]:
    sys.exit("STOP: landscape_families.csv disagrees with benchmark_concentration.json (rerun build/landscape_candidates.py)")
if {r["normalized_name"] for r in _LF} != {r["normalized_name"] for r in _DR if r["is_placeholder"] == "no"}:
    sys.exit("STOP: landscape family names differ from dataset_records names")
import families as _T1
data["land"] = dict(fam={r["normalized_name"]: r["family"] for r in _LF}, dskey={r["normalized_name"]: r["dataset_key"] for r in _LF},
                    famlabel={f: _T1.display(f) for f in {r["family"] for r in _LF}},
                    famflags=_LS["families"]["flagged_list"],
                    cand=[{k: v for k, v in r.items() if k != "record_ids"} for r in _LC], crit=_LS["criteria"], counts=_LS["counts"],
                    r3={k: dict(exact=v["exact_name_papers"], dataset=v["dataset_papers"], prefix=v["family_papers"]) for k, v in json.load(open(p("out/reconcile_counts.json"), encoding="utf-8"))["name_frequencies"].items() if isinstance(v, dict)},
                    sources=dict(families="out/landscape_families.csv", candidates="out/benchmark_candidates.csv", criteria="out/benchmark_candidates.json", script="build/landscape_candidates.py"))
# ---- แท็บ "ความยากที่วัดได้" (28 ต.ค. 2026, Toon สั่ง): อ่านผลจาก difficulty/ ไม่คำนวณใหม่ในแม่แบบ ----
# difficulty/measure.py (HVDM, k=5, Napierala rare rule) -> group_cited.py -> profile_final.py; projection.py -> projections.json
_MZ_ROWS = list(csv.DictReader(open(p("difficulty/difficulty_profile_final.csv"), encoding="utf-8")))
_MZ_SUM = json.load(open(p("difficulty/profile_final_summary.json"), encoding="utf-8"))
_MZ_PROJ = json.load(open(p("difficulty/projections.json"), encoding="utf-8"))
_MZ_DIM = json.load(open(p("difficulty/dimension_profile.json"), encoding="utf-8"))
_TT = {"binary file": "binary", "binarised (rule reproduced)": "binarized", "one-vs-rest (ours)": "ovr"}
for _r in _MZ_ROWS:
    _r["task_type"] = _TT[_r["origin"]]
    _r["key"] = "|".join([_r["file"], _r["source"], _r["task_type"], _r["minority_label"], _r["N"]])
    for _c in ("small_disjuncts", "small_sample", "outlier_flag"):
        _r[_c] = _r[_c] == "True"
    # ตรวจธงซ้ำจากเกณฑ์ที่มีอ้างอิง (group_cited.py)
    if _r["small_disjuncts"] != (float(_r["rare"]) >= 0.20) or _r["outlier_flag"] != (float(_r["outlier"]) > 0.20) \
            or _r["small_sample"] != (float(_r["n_min_per_feature"]) < 10):
        sys.exit(f"STOP: flags in difficulty_profile_final.csv disagree with the cited thresholds for {_r['key']}")
_MZ_B = [r for r in _MZ_ROWS if r["task_type"] != "ovr"]
if {r["key"] for r in _MZ_B} != set(_MZ_PROJ["real"]):
    sys.exit("STOP: projections.json tasks differ from the binary/binarised rows of difficulty_profile_final.csv (rerun difficulty/projection.py)")
if len(_MZ_B) != _MZ_SUM["tasks_binary_binarised"]["n"] or sum(int(r["entries"]) for r in _MZ_B) != _MZ_SUM["entries_binary_binarised"]["n"]:
    sys.exit("STOP: profile_final_summary.json disagrees with difficulty_profile_final.csv (rerun difficulty/profile_final.py)")
for _k, _v in _MZ_PROJ["real"].items():
    _r = next(r for r in _MZ_B if r["key"] == _k)
    if sum(_v["types"].values()) != int(_r["n_min"]) or abs(_v["types"]["O"] / int(_r["n_min"]) - float(_r["outlier"])) > 6e-4:
        sys.exit(f"STOP: point types in projections.json disagree with difficulty_measures for {_k}")
_keep = ("key", "file", "source", "task_type", "minority_label", "N", "n_min", "n_features_raw", "IR", "ir_band", "noise_index",
         "borderline", "outlier", "rare", "safe", "n_min_per_feature", "small_disjuncts", "small_sample", "outlier_flag",
         "profile", "entries", "papers", "version_note")
data["mz"] = dict(rows=[{k: r[k] for k in _keep} for r in _MZ_ROWS], summary=_MZ_SUM,
                  proj=_MZ_PROJ["real"], ill=_MZ_PROJ["illustrations"], proj_meta=_MZ_PROJ["meta"],
                  dim=dict(entry=_MZ_DIM["entry_level"], name=_MZ_DIM["name_level"], tasks=_MZ_DIM["verified_tasks"]["raw"],
                           verif=_MZ_DIM["verifiability_by_bin"], over100=_MZ_DIM["entries_over_100_features"],
                           n_with=_MZ_DIM["entries_with_n_features"], n_without=_MZ_DIM["entries_without_n_features"]),
                  sources=dict(rows="difficulty/difficulty_profile_final.csv", summary="difficulty/profile_final_summary.json",
                               proj="difficulty/projections.json", dim="difficulty/dimension_profile.json",
                               scripts="difficulty/measure.py, group_cited.py, profile_final.py, projection.py, dimension_profile.py"))
# 8 พ.ย. 2026: ตรวจรอบสองกับ mirror เพิ่ม (difficulty/verify_ext.py) + ชื่อที่ยังวัดไม่ได้ (build/name_level_extras.py)
_VX = json.load(open(p("difficulty/verify_ext_summary.json"), encoding="utf-8"))
_NX = json.load(open(p("out/name_level_extras.json"), encoding="utf-8"))
_DL = rcsv("out/names_to_download.csv")
if _VX["verifiable_total"]["entries"] != sum(1 for r in rcsv("difficulty/verifiability_entries.csv") if r["verif"].startswith("V-")):
    sys.exit("STOP: verify_ext_summary.json disagrees with verifiability_entries.csv (rerun difficulty/verify_ext.py)")
if len(_DL) != _NX["not_measured"]["names_to_download"]["names"]:
    sys.exit("STOP: out/names_to_download.csv disagrees with out/name_level_extras.json (rerun build/name_level_extras.py)")
data["mz"]["verify"] = dict(total=_VX["verifiable_total"], new=_VX["newly_verifiable"], status=_VX["status_now"], status28=_VX["status_28oct"],
                            notm=_NX["not_measured"], dl=[[r["normalized_name"], r["name_type"], r["source"], int(r["n_papers"]), int(r["entries"]),
                                                          r["papers"], r["printed_n"], r["printed_features"], r["sources_as_reported"]] for r in _DL],
                            src="difficulty/verify_ext_summary.json, out/name_level_extras.json, out/names_to_download.csv")
# 8 พ.ย. 2026: synthetic เผยแพร่ไหม (build/synthetic_availability.py, รันบนเครื่องที่มี paper/)
_SY = json.load(open(p("out/synthetic_availability.json"), encoding="utf-8"))
if sum(v["entries"] for v in _SY["part_A_by_group"].values()) != DASH["entries"]["by_cat"]["synthetic"]:
    sys.exit("STOP: synthetic_availability.json entries differ from the synthetic entries in dataset_records (rerun build/synthetic_availability.py)")
data["syn"] = dict(_SY, source="out/synthetic_availability.json (build/synthetic_availability.py; scan: out/synthetic_scan.json)")
# 8 พ.ย. 2026: Toon ขอให้ Atlas มีข้อมูล handoff ทั้งหมด -> ฝัง handoff.md (แปลงด้วย build/md2html.py)
import md2html
_HO_MD = open(p("handoff.md"), encoding="utf-8").read()
_HO_HTML, _HO_TOC = md2html.convert(_HO_MD)
data["handoff"] = dict(html=_HO_HTML, toc=_HO_TOC, lines=_HO_MD.count("\n") + 1,
                       conclusions_html=md2html.convert(open(p("CONCLUSIONS.md"), encoding="utf-8").read())[0],
                       status=dict(corpus=DASH["entries"]["by_cat"], names=DASH["names"]["distinct"], verify=_VX["verifiable_total"],
                                   tasks=dict(binary=_MZ_SUM["tasks_binary_binarised"]["n"], ovr=_MZ_SUM["tasks_ovr"]["n"],
                                              entries=_MZ_SUM["entries_binary_binarised"]["n"], papers=_MZ_SUM["entries_binary_binarised_papers"]),
                                   syn=_SY["part_A_by_group"], synB=_SY["part_B"]),
                       source="handoff.md, CONCLUSIONS.md")
# ผลตรวจการกระจุกตามตระกูล (28 ต.ค. 2026): build/family_dependence.py -> out/family_dependence.json
_FD = json.load(open(p("out/family_dependence.json"), encoding="utf-8"))
if _FD["rows"] != ELIG["plain"]["rows"]:
    sys.exit("STOP: family_dependence.json was not computed on the primary set (rerun build/family_dependence.py)")
data["famdep"] = dict(t1={k: _FD["t1"][k] for k in ("pairs", "same_sign", "perm_same_sign_mean", "p_same_sign", "rank_gap", "perm_rank_gap_mean",
                                                   "p_rank_gap", "informative_papers", "informative_rows", "pairs_by_paper", "leave_one_paper_out")},
                      sharing=_FD["t1_by_minority_sharing"], linked=_FD["rows_linked_to_records"], rows=_FD["rows"],
                      source="out/family_dependence.json (build/family_dependence.py; families: out/dataset_families.csv, rule T1)")
# ชนะ/แพ้ทุก metric ที่ paper รายงาน (28 ต.ค. 2026): build/winloss_allmetric.py -> out/winloss_allmetric_*.{json,csv}
_WA = json.load(open(p("out/winloss_allmetric_summary.json"), encoding="utf-8"))
if _WA["crosscheck_rule_A"].get("match", 0) != sum(_WA["crosscheck_rule_A"].values()):
    sys.exit("STOP: all-metric copy of the rule-A metric does not match the earlier extraction")
# Toon 28 Oct 2026: main = plain SMOTE, non-plain comparators apart, MC-MBRC excluded (guard: rows add up)
_wa_np = _WA["non_plain_by_comparator"]
if (_WA["plain_smote_only"]["overall_all_metrics"]["rows"] + sum(v["overall_all_metrics"]["rows"] for v in _wa_np.values())
        != _WA["all_comparators"]["overall_all_metrics"]["rows"]) or "MC-MBRC" not in _WA["excluded"]:
    sys.exit("STOP: all-metric split (plain / non-plain / excluded) does not add up")
data["wl_all"] = dict(all=_WA["all_comparators"], plain=_WA["plain_smote_only"], ruleA=_WA["rule_A_metric_only"],
                      nonplain=_wa_np, excluded=_WA["excluded"], decision=_WA["decision"],
                      per_paper=_WA["per_paper"], rule=_WA["rule"], cross=_WA["crosscheck_rule_A"],
                      source="out/winloss_allmetric_summary.json, _rows.csv, _paper_reported.csv (build/winloss_allmetric.py; raw: ai-draft/outcome/allmetric/*.json)")
# H1-H3 and measured difficulty (29 Oct 2026): build/hypotheses.py, build/difficulty_outcomes.py
_HY = json.load(open(p("out/hypotheses.json"), encoding="utf-8")); _DO = json.load(open(p("out/difficulty_outcomes.json"), encoding="utf-8"))
if _HY["all_metric_plain"]["overall"]["rows"] + sum(1 for _ in []) != _WA["plain_smote_only"]["overall_all_metrics"]["rows"] - _WA["plain_smote_only"]["overall_all_metrics"]["not_comparable"]:
    sys.exit("STOP: hypotheses.json rows differ from the all-metric plain rows")
data["hyp"] = dict(main=_HY["all_metric_plain"], r1=_HY["robust_R1_dataset_majority"], r2=_HY["robust_R2_ruleA"],
                   within=_HY["H1_within_paper_descriptive"], h2=_HY["H2"], h3a=_HY["H3a_granularity"], h3b=_HY["H3b_listed_not_compared"],
                   diff=dict(_DO, robust=_DO["robust_task_majority_noise_per_0.1"]),
                   source="out/hypotheses.json (build/hypotheses.py), out/difficulty_outcomes.json (build/difficulty_outcomes.py)")
# ชนิดระดับชื่อ + ความยากที่วัดได้ของแต่ละชื่อ (29 ต.ค. 2026, Toon สั่งให้แผงชนิดใช้จำนวนที่ normalise แล้ว): build/name_level_types.py
_NT = json.load(open(p("out/name_level_types.json"), encoding="utf-8")); _NTR = rcsv("out/name_level_types.csv")
if _NT["names"] != DASH["names"]["distinct"] or len(_NTR) != _NT["names"] or sum(_NT["by_type"].values()) != _NT["names"] \
        or C.Counter(r["name_type"] for r in _NTR) != C.Counter({k: v for k, v in _NT["by_type"].items() if v}):
    sys.exit("STOP: out/name_level_types.* disagree with each other or with the 771 names (rerun python3 build/name_level_types.py)")
if sum(_NT["by_source"].values()) != _NT["names"] or C.Counter(r["source"] for r in _NTR) != C.Counter({k: v for k, v in _NT["by_source"].items() if v}) \
        or _NT["entry_level_by_source"]["KEEL"] != DASH["provenance"]["repos"]["KEEL"]["total"]:
    sys.exit("STOP: name-level sources in out/name_level_types.* do not add up (rerun python3 build/name_level_types.py)")
if sum(_NT["by_difficulty"].values()) != _NT["names"] or C.Counter(r["difficulty"] for r in _NTR) != C.Counter({k: v for k, v in _NT["by_difficulty"].items() if v}):
    sys.exit("STOP: name-level difficulty counts do not add up to the 771 names (rerun python3 build/name_level_types.py)")
_MOS = json.load(open(p("out/modified_operations_summary.json"), encoding="utf-8"))
if any(_NT["modified_ops"]["by_op"][o]["entries"] != _MOS["tag_entries"][o] or _NT["modified_ops"]["by_op"][o]["names"] != sum(o in r["mod_ops"].split(";") for r in _NTR)
       for o in _NT["modified_ops"]["order"]) or _NT["modified_ops"]["entries"] != _MOS["entries"]:
    sys.exit("STOP: modified_ops in out/name_level_types.json disagrees with out/modified_operations_summary.json or the name rows")
_SI = rcsv("out/name_level_sources.csv")
if len(_SI) != _NT["distinct_sources"]["n"] or {r["source"] for r in _SI} != {x for r in _NTR for x in r["source_ids"].split("; ") if x} \
        or sum(_NT["distinct_sources"]["sources_per_paper"].values()) != _NT["distinct_sources"]["papers"]:
    sys.exit("STOP: out/name_level_sources.csv disagrees with out/name_level_types.* (rerun python3 build/name_level_types.py)")
data["nt"] = dict(sum=_NT, rows=[[r["normalized_name"], r["name_type"], int(r["entries"]), r["entries_by_category"], int(r["n_papers"]), r["papers"],
                                 r["difficulty"], r["measured_tasks"], r["not_measured_reason"], r["source"], r["entries_by_source"], r["source_combo"], r["source_ids"], r["mod_ops"]] for r in _NTR],
                  source="out/name_level_types.csv, out/name_level_types.json (build/name_level_types.py)")
data["manuscript"] = dict(overview=json.load(open(p("manuscript/overview.json"), encoding="utf-8")),
                          html=tex2html.convert(_tex), tex=_tex)
js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
open(p("out/explorer_data.json"), "w", encoding="utf-8").write(js)
tpl = open(p("build/atlas_template.html"), encoding="utf-8").read()
open(p("out/dataset-atlas.html"), "w", encoding="utf-8").write(tpl.replace("__DATA__", js.replace("</", "<\\/")))
print("datasets", len(out_ds), "papers", len(pp), "dataset rows", len(FD), "outcome rows", len(FO))
print("eligibility", json.dumps(ELIG))
print("dash entries", DASH["entries"]["by_cat"], "names", DASH["names"]["distinct"], DASH["names"]["single_paper"],
      "size", DASH["size_variation"]["names_with_size_in_2plus_papers"], DASH["size_variation"]["names_with_more_than_one_size"],
      "prov", {k: (v["total"], v["by_cat"]) for k, v in _prov.items()}, "mixed", _mixed)
