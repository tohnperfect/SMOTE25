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
import collections as C, csv, json, os, sys
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
if _RCJ["sources"]["outcomes"]["sha256"] != RC.sha(RC.SRC["outcomes"]):
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
_xc = [r for r in FO if not r["eligible"]]
_typ = lambda L: {t: _tal([r for r in L if r["how_obtained"] == t]) for t in CATS + ["unmatched"] if any(r["how_obtained"] == t for r in L)}
DASH = dict(
    corpus=dict(papers_total=S["papers_total"], papers_empirical=S["papers_empirical"], non_empirical=S["non_empirical"]),
    entries=dict(total=len(FD), by_cat={c: _cat.get(c, 0) for c in CATS},
                 named=sum(1 for r in FD if (r["name"] or "") and not RC.PLACEHOLDER_RE.match(r["name"]))),
    names=dict(distinct=len(out_ds), single_paper=sum(1 for x in out_ds if len(x[2]) == 1),
               families={f: dict(exact=v["exact_name_papers"], family=v["family_prefix_papers"])
                         for f, v in _RCJ["name_frequencies"].items() if isinstance(v, dict)}),
    provenance=dict(repos=_prov, mixed_group_level=_mixed),
    size_variation=dict(names_with_size_in_2plus_papers=len(_two), names_with_more_than_one_size=len(_diff), examples=_ex),
    granularity=dict(C.Counter(x["results_granularity"] for x in FS["papers"])), granularity_papers=len(FS["papers"]),
    baseline=dict(C.Counter(x["smote_kind"] for x in FS["papers"])),
    by_type=dict(plain=_typ([r for r in FO if r["eligible"] and r["smote_kind"] == RC.PLAIN]),
                 wrapper=_typ([r for r in FO if r["eligible"] and r["smote_kind"] == RC.WRAP]), excluded=_typ(_xc)),
    excluded_groups=[dict(paper=k, reason=("aggregate" if all(r["excluded_reason"].startswith("aggregate") for r in _xc if r["paper"] == k) else "cross-table"),
                          **_tal([r for r in _xc if r["paper"] == k])) for k in sorted({r["paper"] for r in _xc})],
)
# ---- Dataset Explorer (19 ต.ค. 2026): ระเบียนราย entry จาก build/dataset_records.py เฉพาะด้าน dataset ไม่มีผลเทียบ ----
_DRS = json.load(open(p("out/dataset_records_summary.json"), encoding="utf-8"))
if not all(v["ok"] for v in _DRS["checks"].values()):
    sys.exit("STOP: dataset_records_summary.json has failing checks; run python3 build/dataset_records.py")
if _DRS["sources"]["datasets"]["sha256"] != RC.sha(RC.SRC["datasets"]):
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
data = dict(datasets=out_ds, papers=pp, summary=S, dash=DASH, dx=DX,
            usage=dict(listed_total=len(FD), covered_by_aggregate=U["covered_by_aggregate"], aggregate_entry_count=U["aggregate_entry_count"]),
            outcome=dict(papers=FS["papers"], rows=[{k2: r[k2] for k2 in keep} for r in FO], eligibility=ELIG))
# แท็บร่าง manuscript (เพิ่ม 18 ต.ค. 23:55 ตามที่ Toon ขอ เพื่อนำเสนออาจารย์)
sys.path.insert(0, p("build")); import tex2html
_tex = open(p("manuscript/data-section-draft.tex"), encoding="utf-8").read()
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
