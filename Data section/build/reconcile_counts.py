"""reconcile_counts.py  กระทบยอดตัวเลขที่ไม่ตรงกัน 4 เรื่อง (สร้าง 19 ต.ค. 2026 ตามที่ Toon อนุมัติ)

อ่านอย่างเดียว (ไม่แก้ไฟล์ต้นทาง)
  out/verified_datasets.csv   1 แถว = 1 dataset entry ใน 1 paper    ฟิลด์: paper, name, n_instances, how_obtained_final
  out/verified_outcomes.csv   1 แถว = ผลเทียบวิธีที่เสนอกับ SMOTE    ฟิลด์: paper, dataset, match, how_obtained, smote_kind, raw_sign, table, page
  out/full_summary.json       ส่วน "papers" 1 รายการต่อ paper        ฟิลด์: key, smote_kind, results_granularity, rows_with_smote
  ใช้ norm() จาก build/analyse_dataset_usage.py ตัวเดียวกับที่ Atlas และ draft ใช้

เขียน
  out/reconcile_counts.json   ถ้ามีไฟล์อยู่แล้วและเนื้อหาต่างจากที่จะเขียน จะหยุด ไม่เขียนทับ
                              ต้องสั่ง --overwrite เองหลังตรวจแล้ว

วิธีรัน (จาก Data section/)
  python3 build/reconcile_counts.py              เขียน out/reconcile_counts.json และพิมพ์สรุป
  python3 build/reconcile_counts.py --check      พิมพ์สรุปอย่างเดียว ไม่เขียนไฟล์
  python3 build/reconcile_counts.py --overwrite  เขียนทับไฟล์ผลเดิม (ใช้เมื่อตั้งใจเท่านั้น)

ผลลัพธ์ deterministic: ไม่มีการสุ่ม ทุกรายการเรียงตามตัวอักษร ไม่ใส่เวลาที่รันลงไฟล์ (มีแต่ sha256 ของไฟล์ต้นทาง)

กติกาการนับ (ตัดสินโดย Toon 19 ต.ค. 2026)
  R1  ชื่อ dataset หลักนับเฉพาะ entry ที่มีชื่อจริง ตัด placeholder ที่ผู้อ่านเขียนบรรยายแทนชื่อ
      ตรวจจับด้วย PLACEHOLDER_RE (ข้อความในวงเล็บเหลี่ยมที่มีคำว่า "not named") ตอนนี้ตรงแถวเดียวคือ Tomek Links
      แถวนั้นยังอยู่ใน CSV และยังนับใน 1,654 entries ทั้งหมด
  R2  ชื่อที่ต่างกัน = จำนวนค่า norm(name) ที่ต่างกัน norm() แปลงเป็นตัวเล็ก ตัดข้อความในวงเล็บ รวม _ และช่องว่าง
      ไม่ได้ตัดขีดหรือจุด (ตัวเลขแบบตัดเครื่องหมายทั้งหมดรายงานไว้เพื่อเทียบเท่านั้น)
  R3  ความถี่ของชื่อ นับ paper ที่ต่างกัน  exact = norm(name) ตรงกับชื่อ  family = norm(name) ขึ้นต้นด้วยชื่อ (prefix)
  R4  ผลเทียบหลักคือ plain SMOTE รายชุด แถวที่ dataset ขึ้นต้นด้วย Mean/Average คือค่ารวมหลายชุด (AGG_RE)
      แยกรายงานต่างหาก ไม่นับเป็นผลรายชุด (ตอนนี้ตรงแถวเดียวคือ KNNOR)
  R5  plain SMOTE กับ SMOTE แบบห่อ (wrapper) รายงานแยกกันเสมอ ไม่รวมกัน
  R6  แถวที่ช่อง table อ้างมากกว่าหนึ่งตารางเป็น "candidate" เท่านั้น (regex จับได้ทั้งกรณีที่ dataset คนละชุดอยู่คนละตาราง)
      ผลตรวจด้วยมือว่าเป็นการจับคู่ค่าวิธีที่เสนอกับ SMOTE ข้ามตารางจริงหรือไม่ อยู่ใน CROSS_TABLE_REVIEW ไม่ลบแถว แค่รายงาน
  R7  (เพิ่ม 19 ต.ค. 2026 รอบ final) ชุดเทียบแบ่งเป็น partition ที่ไม่ทับกัน 3 ส่วน ไม่รวมกันเด็ดขาด
      primary  = plain SMOTE, ไม่ใช่แถวค่ารวม (R4), paper ไม่อยู่ใน cross-table ที่ยืนยันแล้ว (R6)
      wrapper  = SMOTE แบบห่อ, ไม่ใช่แถวค่ารวม, paper ไม่อยู่ใน cross-table ที่ยืนยันแล้ว
      excluded = แถวค่ารวม (R4) + แถวของ paper ที่ยืนยันว่าจับคู่ข้ามตาราง (R6) เก็บไว้ audit
      ตรวจว่า primary + wrapper + excluded = แถวทั้งหมด และไม่มีแถวใดอยู่สองส่วน
  standard = how_obtained เป็น original หรือ repository-defined
"""
import argparse, csv, hashlib, json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(HERE, *a)
sys.path.insert(0, P("build"))
import analyse_dataset_usage as A  # noqa: E402  norm() ตัวเดียวกับ Atlas

SRC = {"datasets": "out/verified_datasets.csv", "outcomes": "out/verified_outcomes.csv", "summary": "out/full_summary.json"}
OUT = "out/reconcile_counts.json"
PLACEHOLDER_RE = re.compile(r"^\s*\[.*\bnot named\b.*\]\s*$", re.I)
AGG_RE = re.compile(r"^\s*(mean|average|avg)\b", re.I)
TABLE_RE = re.compile(r"\bTable\s+[A-Z]?\d+|\bTable\s+[IVXL]+\b", re.I)
STD = {"original", "repository-defined"}
PLAIN, WRAP = "plain SMOTE", "SMOTE variant (multiclass/ensemble wrapper)"
FAMILIES = ["yeast", "ecoli", "glass"]
# ผลตรวจด้วยมือ 19 ต.ค. 2026 จากช่อง table ใน verified_outcomes.csv และ PDF (RBBoost)
CROSS_TABLE_REVIEW = {
    "RBBoost / Random Balance": "cross-table pair: RB-B from Supplementary Table 11 (Boosting family) vs ESM from Supplementary Table 3 (Data-processing family); same protocol per main paper p.101-102 but the paper never compares RB-B with ESM directly",
    "AMDO": "not cross-table: numeric datasets in Table 6, nominal/mixed in Table 9; each pair from one table",
    "EasyEnsemble / BalanceCascade": "not cross-table: easy tasks in Table X, hard tasks in Table XI; each pair from one table",
    "NROMM": "not cross-table: all pairs from Supplementary Table 8; main Table 3 repeats 7 rows",
    "SMOTE-ENN / SMOTE-Tomek": "not cross-table: pairs from Table 4; Table 5 searched only for best_other",
}

# ตัวเลขที่ draft หรือ handoff เคยพิมพ์ไว้ ใช้ตรวจว่ายังทำซ้ำได้ (ไม่ใช่ค่าที่ต้องบังคับให้ได้)
EXPECTED = {
    "entries_total": 1654, "entries_named": 1653, "distinct_names": 771, "single_paper_names": 546,
    "distinct_names_incl_placeholder": 772, "single_paper_names_incl_placeholder": 547,
    "yeast_family_papers": 39, "ecoli_family_papers": 39, "glass_family_papers": 36,
    "outcome_rows_all": 835, "outcome_rows_plain_incl_aggregate": 542, "outcome_papers_plain_incl_aggregate": 31,
    "plain_per_dataset_rows": 541, "plain_per_dataset_papers": 30,
    "paper_level_plain": 44, "paper_level_wrapper": 13, "paper_level_none": 16,
    "wrapper_repository_defined_rows": 63,
    # R7 partitions (เพิ่ม 19 ต.ค. 2026 รอบ final)
    "primary_rows": 541, "primary_papers": 30,
    "wrapper_eligible_rows": 207, "wrapper_eligible_papers": 12,
    "wrapper_eligible_proposed_higher": 175, "wrapper_eligible_smote_higher": 26, "wrapper_eligible_equal": 6,
    "wrapper_eligible_original": 173, "wrapper_eligible_modified": 30, "wrapper_eligible_synthetic": 4,
    "wrapper_eligible_repository_defined": 0, "wrapper_eligible_not_stated": 0, "wrapper_eligible_unmatched": 0,
    "wrapper_eligible_types_sum_equals_rows": True, "wrapper_eligible_signs_sum_equals_rows": True,
    "excluded_rows": 87, "excluded_aggregate_rows": 1, "excluded_cross_table_rows": 86,
    "excluded_cross_table_repository_defined": 63, "excluded_cross_table_not_stated": 17, "excluded_cross_table_original": 6,
    "partitions_cover_all_rows_once": True,
}

def sha(path):
    h = hashlib.sha256()
    with open(P(path), "rb") as fh: h.update(fh.read())
    return h.hexdigest()

def rcsv(path):
    with open(P(path), encoding="utf-8-sig", newline="") as fh: return list(csv.DictReader(fh))

def signs(rows):
    c = Counter(r["raw_sign"] for r in rows)
    return {"rows": len(rows), "papers": len({r["paper"] for r in rows}),
            "proposed_higher": c["+"], "smote_higher": c["-"], "equal": c["="]}

def by_type(rows):
    return {t: signs([r for r in rows if r["how_obtained"] == t]) for t in sorted({r["how_obtained"] for r in rows})}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="print only, do not write")
    ap.add_argument("--overwrite", action="store_true", help="replace an existing different output file")
    a = ap.parse_args()

    D, O = rcsv(SRC["datasets"]), rcsv(SRC["outcomes"])
    S = json.load(open(P(SRC["summary"]), encoding="utf-8"))
    PP = sorted(S["papers"], key=lambda p: p["key"])
    R = {"_about": "สร้างโดย build/reconcile_counts.py อ่านอย่างเดียวจากไฟล์ใน sources ดูกติกา R1-R6 ใน docstring ของสคริปต์",
         "sources": {k: {"path": v, "sha256": sha(v)} for k, v in sorted(SRC.items())}}

    # ---------------- 1. dataset entries and names (R1, R2) ----------------
    placeholders = [{"csv_line": i + 2, "paper": r["paper"], "name": r["name"], "how_obtained_final": r["how_obtained_final"]}
                    for i, r in enumerate(D) if PLACEHOLDER_RE.match(r["name"] or "")]
    empty = [{"csv_line": i + 2, "paper": r["paper"]} for i, r in enumerate(D) if not (r["name"] or "").strip()]
    def name_map(rows):
        m = defaultdict(set)
        for r in rows: m[A.norm(r["name"])].add(r["paper"])
        return m
    named = [r for r in D if (r["name"] or "").strip() and not PLACEHOLDER_RE.match(r["name"])]
    m_named, m_all = name_map(named), name_map(D)
    R["names"] = {
        "rule": "R1 + R2: exclude placeholder descriptions; distinct values of analyse_dataset_usage.norm(name)",
        "entries_total": len(D), "entries_named": len(named), "papers": len({r["paper"] for r in D}),
        "excluded_placeholder_rows": placeholders, "empty_name_rows": empty,
        "distinct_names": len(m_named), "single_paper_names": sum(len(v) == 1 for v in m_named.values()),
        "distinct_names_incl_placeholder": len(m_all),
        "single_paper_names_incl_placeholder": sum(len(v) == 1 for v in m_all.values()),
        "distinct_if_all_punctuation_removed": len({re.sub(r"[^a-z0-9]", "", k) for k in m_named}),
        "norm_definition": "lower-case; drop text in parentheses; collapse underscores and whitespace; hyphens and dots kept",
    }

    # ---------------- 2. name frequencies (R3) ----------------
    fam = {}
    for f in FAMILIES:
        keys = sorted(k for k in m_named if k.startswith(f))
        exact = sorted(m_named.get(f, set()))
        prefix = sorted(set().union(*[m_named[k] for k in keys])) if keys else []
        fam[f] = {"exact_name_papers": len(exact), "family_prefix_papers": len(prefix), "prefix_name_keys": keys,
                  "papers_exact": exact, "papers_only_via_prefix": sorted(set(prefix) - set(exact))}
    R["name_frequencies"] = {"rule": "R3: papers per name; exact = norm(name)==f, family = norm(name).startswith(f)", **fam}

    # ---------------- 3. outcome rows (R4, R5) ----------------
    agg = [r for r in O if AGG_RE.match(r["dataset"] or "")]
    agg_ids = {id(r) for r in agg}
    plain = [r for r in O if r["smote_kind"] == PLAIN]
    wrap = [r for r in O if r["smote_kind"] == WRAP]
    plain_ds = [r for r in plain if id(r) not in agg_ids]
    other_kind = sorted({r["smote_kind"] for r in O} - {PLAIN, WRAP})
    papers_plain_ds = sorted({r["paper"] for r in plain_ds})
    std_papers = sorted({r["paper"] for r in plain_ds if r["how_obtained"] in STD})
    std_rows = [r for r in plain_ds if r["how_obtained"] in STD]
    R["outcomes"] = {
        "rule": "R4 + R5: plain and wrapper never pooled; rows whose dataset starts with Mean/Average are aggregate, reported separately",
        "all_rows": signs(O), "unexpected_smote_kinds": other_kind,
        "aggregate_rows": [{"csv_line": O.index(r) + 2, "paper": r["paper"], "dataset": r["dataset"], "smote_kind": r["smote_kind"],
                            "metric": r["metric"], "table": r["table"], "page": r["page"], "proposed": r["proposed"], "smote": r["smote"],
                            "raw_sign": r["raw_sign"]} for r in agg],
        "plain_incl_aggregate": signs(plain),
        "plain_per_dataset": signs(plain_ds), "plain_per_dataset_by_type": by_type(plain_ds),
        "plain_per_dataset_standard": {**signs(std_rows), "papers_with_standard_rows": len(std_papers),
                                       "papers_without_standard_rows": sorted(set(papers_plain_ds) - set(std_papers))},
        "wrapper": signs(wrap), "wrapper_by_type": by_type(wrap),
        "wrapper_papers": {p: n for p, n in sorted(Counter(r["paper"] for r in wrap).items())},
    }

    # ---------------- 4. paper-level baseline vs rows ----------------
    has_rows = Counter(r["paper"] for r in O)
    has_ds_rows = Counter(r["paper"] for r in O if id(r) not in agg_ids)
    pl = {}
    for kind in sorted({p["smote_kind"] for p in PP}):
        grp = [p for p in PP if p["smote_kind"] == kind]
        pl[kind] = {
            "papers": len(grp),
            "with_outcome_rows": sorted(p["key"] for p in grp if has_rows[p["key"]]),
            "with_per_dataset_rows": sorted(p["key"] for p in grp if has_ds_rows[p["key"]]),
            "without_outcome_rows": [{"paper": p["key"], "results_granularity": p["results_granularity"]}
                                     for p in grp if not has_rows[p["key"]]],
            "aggregate_rows_only": sorted(p["key"] for p in grp if has_rows[p["key"]] and not has_ds_rows[p["key"]]),
        }
        for k2 in ("with_outcome_rows", "with_per_dataset_rows", "aggregate_rows_only"):
            pl[kind]["n_" + k2] = len(pl[kind][k2])
        pl[kind]["n_without_outcome_rows"] = len(pl[kind]["without_outcome_rows"])
    with_baseline = [p for p in PP if p["smote_kind"] != "not a baseline"]
    no_pair = [p["key"] for p in with_baseline if not has_ds_rows[p["key"]]]
    R["paper_level"] = {
        "rule": "smote_kind per paper from full_summary.json (classified from smote_name_as_printed); rows from verified_outcomes.csv",
        "by_kind": pl,
        "papers_with_smote_baseline": len(with_baseline),
        "papers_with_baseline_but_no_per_dataset_pair": sorted(no_pair), "n_no_per_dataset_pair": len(no_pair),
        "rows_with_smote_consistent": all(p["rows_with_smote"] == has_rows[p["key"]] for p in PP),
        "note_two_meanings_of_44": "44 = papers whose SMOTE baseline is plain SMOTE (paper level); also 44 = papers with any outcome row (31 plain + 13 wrapper). Coincidence, different sets.",
    }

    # ---------------- 5. repository-defined by kind and paper (R6) ----------------
    rep = {}
    for kind, rows in ((PLAIN, plain_ds), (WRAP, wrap)):
        sub = [r for r in rows if r["how_obtained"] == "repository-defined"]
        rep[kind] = {"total": signs(sub),
                     "by_paper": {p: signs([r for r in sub if r["paper"] == p]) for p in sorted({r["paper"] for r in sub})}}
    cross = defaultdict(list)
    for i, r in enumerate(O):
        tabs = {t.lower() for t in TABLE_RE.findall(r["table"] or "")}
        if len(tabs) > 1: cross[r["paper"]].append(i + 2)
    R["repository_defined"] = {"rule": "how_obtained == repository-defined; plain per-dataset vs wrapper reported separately", **rep}
    R["cross_table_pairs"] = {"rule": "R6: candidates = rows whose table field names more than one table; verdict from CROSS_TABLE_REVIEW",
                              "candidates": {p: {"rows": len(v), "csv_lines": [v[0], v[-1]],
                                                 "review": CROSS_TABLE_REVIEW.get(p, "NOT REVIEWED")} for p, v in sorted(cross.items())},
                              "confirmed_cross_table": sorted(p for p in cross if CROSS_TABLE_REVIEW.get(p, "").startswith("cross-table")),
                              "unreviewed": sorted(p for p in cross if p not in CROSS_TABLE_REVIEW)}

    # ---------------- R7: disjoint comparison partitions ----------------
    confirmed = {p for p in cross if CROSS_TABLE_REVIEW.get(p, "").startswith("cross-table")}
    def part(r):
        if id(r) in agg_ids: return "excluded_aggregate"
        if r["paper"] in confirmed: return "excluded_cross_table"
        if r["smote_kind"] == PLAIN: return "primary"
        if r["smote_kind"] == WRAP: return "wrapper"
        return "unassigned"
    PART = defaultdict(list)
    for r in O: PART[part(r)].append(r)
    weg = PART["wrapper"]; wtypes = Counter(r["how_obtained"] for r in weg); wsig = signs(weg)
    xc = PART["excluded_cross_table"]; xtypes = Counter(r["how_obtained"] for r in xc)
    R["partitions"] = {
        "rule": "R7: primary = plain per-dataset, wrapper = eligible wrapper, excluded = aggregate (R4) + confirmed cross-table (R6); never pooled",
        "primary": {**signs(PART["primary"]), "by_type": by_type(PART["primary"])},
        "wrapper_eligible": {**wsig, "by_type": by_type(weg), "papers_list": sorted({r["paper"] for r in weg})},
        "excluded": {"rows": len(PART["excluded_aggregate"]) + len(xc),
                     "aggregate": [{"csv_line": O.index(r) + 2, "paper": r["paper"], "dataset": r["dataset"], "smote_kind": r["smote_kind"]}
                                   for r in PART["excluded_aggregate"]],
                     "cross_table": {**signs(xc), "papers": sorted({r["paper"] for r in xc}),
                                     "by_type": dict(sorted(xtypes.items())),
                                     "smote_kind": dict(sorted(Counter(r["smote_kind"] for r in xc).items()))}},
        "unassigned_rows": len(PART["unassigned"]),
    }
    covered = sum(len(v) for v in PART.values())

    # ---------------- checks against previously printed figures ----------------
    got = {
        "entries_total": R["names"]["entries_total"], "entries_named": R["names"]["entries_named"],
        "distinct_names": R["names"]["distinct_names"], "single_paper_names": R["names"]["single_paper_names"],
        "distinct_names_incl_placeholder": R["names"]["distinct_names_incl_placeholder"],
        "single_paper_names_incl_placeholder": R["names"]["single_paper_names_incl_placeholder"],
        "yeast_family_papers": fam["yeast"]["family_prefix_papers"], "ecoli_family_papers": fam["ecoli"]["family_prefix_papers"],
        "glass_family_papers": fam["glass"]["family_prefix_papers"],
        "outcome_rows_all": len(O), "outcome_rows_plain_incl_aggregate": len(plain),
        "outcome_papers_plain_incl_aggregate": len({r["paper"] for r in plain}),
        "plain_per_dataset_rows": len(plain_ds), "plain_per_dataset_papers": len(papers_plain_ds),
        "paper_level_plain": pl.get(PLAIN, {}).get("papers"), "paper_level_wrapper": pl.get(WRAP, {}).get("papers"),
        "paper_level_none": pl.get("not a baseline", {}).get("papers"),
        "wrapper_repository_defined_rows": rep[WRAP]["total"]["rows"],
        "primary_rows": len(PART["primary"]), "primary_papers": len({r["paper"] for r in PART["primary"]}),
        "wrapper_eligible_rows": wsig["rows"], "wrapper_eligible_papers": wsig["papers"],
        "wrapper_eligible_proposed_higher": wsig["proposed_higher"], "wrapper_eligible_smote_higher": wsig["smote_higher"],
        "wrapper_eligible_equal": wsig["equal"],
        "wrapper_eligible_original": wtypes["original"], "wrapper_eligible_modified": wtypes["modified"],
        "wrapper_eligible_synthetic": wtypes["synthetic"], "wrapper_eligible_repository_defined": wtypes["repository-defined"],
        "wrapper_eligible_not_stated": wtypes["not stated"], "wrapper_eligible_unmatched": wtypes["unmatched"],
        "wrapper_eligible_types_sum_equals_rows": sum(wtypes.values()) == wsig["rows"]
            and wtypes["original"] + wtypes["modified"] + wtypes["synthetic"] == wsig["rows"],
        "wrapper_eligible_signs_sum_equals_rows": wsig["proposed_higher"] + wsig["smote_higher"] + wsig["equal"] == wsig["rows"],
        "excluded_rows": len(PART["excluded_aggregate"]) + len(xc), "excluded_aggregate_rows": len(PART["excluded_aggregate"]),
        "excluded_cross_table_rows": len(xc), "excluded_cross_table_repository_defined": xtypes["repository-defined"],
        "excluded_cross_table_not_stated": xtypes["not stated"], "excluded_cross_table_original": xtypes["original"],
        "partitions_cover_all_rows_once": covered == len(O) and not PART["unassigned"]
            and len({id(r) for v in PART.values() for r in v}) == len(O),
    }
    R["checks"] = {k: {"expected": EXPECTED[k], "got": got[k], "ok": EXPECTED[k] == got[k]} for k in sorted(EXPECTED)}

    text = json.dumps(R, ensure_ascii=False, indent=1, sort_keys=False) + "\n"
    bad = [k for k, v in R["checks"].items() if not v["ok"]]
    print(f"checks: {len(R['checks']) - len(bad)}/{len(R['checks'])} ok" + (f"; NOT ok: {bad}" if bad else ""))
    for k, v in R["checks"].items(): print(f"  {k:42s} expected {v['expected']!s:>5}  got {v['got']!s:>5}  {'ok' if v['ok'] else 'DIFF'}")
    if a.check: return 0
    out = P(OUT)
    if os.path.exists(out):
        if open(out, encoding="utf-8").read() == text:
            print(f"{OUT} unchanged"); return 0
        if not a.overwrite:
            print(f"STOP: {OUT} exists with different content. Inspect it, then rerun with --overwrite if intended."); return 2
    with open(out, "w", encoding="utf-8", newline="\n") as fh: fh.write(text)
    print(f"wrote {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
