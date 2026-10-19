"""dataset_records.py  ระเบียน dataset ราย entry พร้อม ID คงที่ สำหรับ Dataset Explorer (เพิ่ม 19 ต.ค. 2026)

ขอบเขต: ข้อมูลด้าน dataset เท่านั้น ไม่มี metric ผลเทียบ หรือแพ้ชนะ

อ่านอย่างเดียว
  out/verified_datasets.csv   1 แถว = 1 dataset entry ใน 1 paper (ไม่แก้)
  out/section7_key_map.csv    paper_id (P001...), bibkey, ชื่อเรื่อง ของแต่ละ paper key
  out/full_summary.json       ส่วน papers: ir_definition และ characteristics_table ระดับ paper
  build/analyse_dataset_usage.py norm()   build/reconcile_counts.py PLACEHOLDER_RE

เขียน
  out/dataset_records.csv           1 แถวต่อ entry ทั้ง 1,654 แถว ไม่รวมแถวแม้ชื่อ normalise ตรงกัน
  out/dataset_records_summary.json  ตัวนับ ความครบของแต่ละช่อง checks และ sha256 ของไฟล์ต้นทาง
  ถ้าไฟล์ผลมีอยู่และเนื้อหาต่าง จะหยุด ต้องสั่ง --overwrite เอง

วิธีรัน (จาก Data section/)
  python3 build/dataset_records.py            เขียนไฟล์ผล (ถ้าเหมือนเดิมจะบอก unchanged)
  python3 build/dataset_records.py --check    คำนวณและตรวจ ไม่เขียนไฟล์
  python3 build/dataset_records.py --overwrite

record_id = <paper_id>-D<ลำดับ 3 หลัก> ลำดับคือตำแหน่งของ entry ภายใน paper ตามลำดับแถวใน verified_datasets.csv
  คงที่ตราบที่ verified_datasets.csv ไม่เปลี่ยนลำดับแถว (sha256 ของไฟล์ต้นทางเก็บไว้ใน summary ใช้ตรวจ)
  ถ้าแก้ CSV ต้นทางแล้วลำดับเปลี่ยน ID จะเปลี่ยนตาม ต้องทำตาราง mapping เก่า-ใหม่ก่อนใช้ต่อ

กติกา
  - ค่าที่ paper พิมพ์เก็บตามตัวอักษร ไม่แปลง ไม่เติม ช่องว่างหรือ "not stated in paper" = ไม่รายงาน
  - ค่าตัวเลข "parse ได้" เมื่อเป็นตัวเลขล้วน (มี , คั่นหลักได้) นอกนั้นนับว่า "รายงานแต่ไม่ใช่ตัวเลขเดี่ยว"
  - IR เก็บตามที่พิมพ์ คู่กับนิยาม IR ระดับ paper ไม่คำนวณ IR ใหม่ และไม่ถือว่าค่า IR ข้าม paper เทียบกันได้
  - normalized_name จาก norm() ใช้จัดกลุ่มเพื่อดูเท่านั้น ไม่ได้แปลว่าเป็นข้อมูลชุดเดียวกัน
  - แถว placeholder (คำบรรยายแทนชื่อ R1) ไม่มี normalized_name และไม่นับในจำนวนชื่อ
  - ไม่มีช่อง version แยกในแหล่งข้อมูล ข้อมูล version/variant/การดัดแปลงอยู่ใน group_in_paper และ preprocessing_note
"""
import argparse, csv, hashlib, io, json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(HERE, *a)
sys.path.insert(0, P("build"))
import analyse_dataset_usage as A   # noqa: E402
import reconcile_counts as RC       # noqa: E402

SRC = {"datasets": "out/verified_datasets.csv", "papers": "out/section7_key_map.csv", "summary": "out/full_summary.json"}
OUT_CSV, OUT_JSON = "out/dataset_records.csv", "out/dataset_records_summary.json"
NUM_RE = re.compile(r"\d[\d,]*(\.\d+)?")
CATS = ["original", "repository-defined", "modified", "synthetic", "not stated"]
EXPECTED = {"entries": 1654, "named_entries": 1653, "normalized_names": 771, "papers_with_entries": 73,
            "original": 534, "repository-defined": 470, "modified": 331, "synthetic": 120, "not stated": 199}
FIELDS = ["record_id", "paper_id", "paper_key", "bibkey", "paper_title", "year", "source_csv_line", "entry_ordinal_in_paper",
          "name_as_reported", "normalized_name", "is_placeholder", "group_in_paper", "source_as_reported",
          "n_instances", "n_features", "n_classes", "n_minority", "n_majority", "class_distribution",
          "ir_as_printed", "ir_definition_paper", "characteristics_table_paper",
          "category", "category_basis", "category_by_reader", "preprocessing_note", "evidence_ref", "verified_page", "value_status"]
# ช่องที่รายงานความครบ: (ช่อง, ชนิด)
CHAR = [("source_as_reported", "text"), ("group_in_paper", "text"), ("n_instances", "num"), ("n_features", "num"),
        ("n_classes", "num"), ("n_minority", "num"), ("n_majority", "num"), ("class_distribution", "text"),
        ("ir_as_printed", "ir"), ("preprocessing_note", "text"), ("evidence_ref", "text")]

def sha(path):
    with open(P(path), "rb") as fh: return hashlib.sha256(fh.read()).hexdigest()

def missing(v):
    v = (v or "").strip()
    return v == "" or v.lower() in ("none", "null") or v.lower().startswith("not stated in paper")

def build():
    D = list(csv.DictReader(open(P(SRC["datasets"]), encoding="utf-8-sig", newline="")))
    K = {r["data_section_key"]: r for r in csv.DictReader(open(P(SRC["papers"]), encoding="utf-8-sig", newline=""))}
    FS = {p["key"]: p for p in json.load(open(P(SRC["summary"]), encoding="utf-8"))["papers"]}
    ordn = Counter(); rows = []
    for i, r in enumerate(D):
        k = r["paper"]; ordn[k] += 1
        if k not in K: sys.exit(f"STOP: paper key {k!r} not in section7_key_map.csv")
        ph = bool(RC.PLACEHOLDER_RE.match(r["name"] or ""))
        fs = FS.get(k, {})
        rows.append({
            "record_id": f'{K[k]["paper_id"]}-D{ordn[k]:03d}', "paper_id": K[k]["paper_id"], "paper_key": k,
            "bibkey": K[k]["bibkey"], "paper_title": K[k]["section7_title"], "year": K[k]["year"],
            "source_csv_line": i + 2, "entry_ordinal_in_paper": ordn[k],
            "name_as_reported": r["name"], "normalized_name": "" if ph else A.norm(r["name"]), "is_placeholder": "yes" if ph else "no",
            "group_in_paper": r["group"], "source_as_reported": r["source_repo"],
            "n_instances": r["n_instances"], "n_features": r["n_features"], "n_classes": r["n_classes"],
            "n_minority": r["n_minority"], "n_majority": r["n_majority"], "class_distribution": r["class_distribution"],
            "ir_as_printed": r["ir_printed"], "ir_definition_paper": fs.get("ir_definition", ""),
            "characteristics_table_paper": fs.get("characteristics_table", ""),
            "category": r["how_obtained_final"], "category_basis": r["how_basis"], "category_by_reader": r["how_obtained"],
            "preprocessing_note": r["how_obtained_detail"], "evidence_ref": r["ref"], "verified_page": r["verified_page"],
            "value_status": r["value_status"]})
    return D, rows

def summarize(rows):
    n = len(rows); named = [r for r in rows if r["is_placeholder"] == "no"]
    names = defaultdict(list)
    for r in named: names[r["normalized_name"]].append(r)
    comp = {}
    for f, kind in CHAR:
        rep = [r for r in rows if not missing(r[f])]
        c = {"denominator": n, "reported": len(rep), "missing": n - len(rep)}
        if kind == "num":
            c["numeric"] = sum(1 for r in rep if NUM_RE.fullmatch(r[f].strip()))
            c["reported_non_numeric"] = c["reported"] - c["numeric"]
        if kind == "ir":
            c["numeric_single_value"] = sum(1 for r in rep if NUM_RE.fullmatch(r[f].strip()))
            c["ratio_form"] = sum(1 for r in rep if ":" in r[f])
            c["other_form"] = c["reported"] - c["numeric_single_value"] - c["ratio_form"]
            c["with_paper_definition_stated"] = sum(1 for r in rep if not missing(r["ir_definition_paper"]))
            c["with_paper_definition_not_stated"] = c["reported"] - c["with_paper_definition_stated"]
        comp[f] = c
    # ชื่อ normalise ที่มีหลาย paper และค่าที่พิมพ์ต่างกัน (แค่ชี้ ไม่ตัดสินว่าเป็นคนละชุด)
    conflicts = Counter()
    for k, L in names.items():
        if len({r["paper_key"] for r in L}) < 2: continue
        for f in ("n_instances", "n_features", "n_classes", "ir_as_printed"):
            if len({r[f].strip() for r in L if not missing(r[f])}) > 1: conflicts[f] += 1
    ir_papers = Counter("stated" if not missing(p) else "not stated"
                        for p in {r["paper_key"]: r["ir_definition_paper"] for r in rows}.values())
    got = {"entries": n, "named_entries": len(named), "normalized_names": len(names),
           "papers_with_entries": len({r["paper_key"] for r in rows}), **{c: sum(r["category"] == c for r in rows) for c in CATS}}
    ids = [r["record_id"] for r in rows]
    checks = {k: {"expected": EXPECTED[k], "got": got[k], "ok": EXPECTED[k] == got[k]} for k in EXPECTED}
    checks["record_ids_unique"] = {"expected": True, "got": len(set(ids)) == len(ids), "ok": len(set(ids)) == len(ids)}
    checks["no_unexpected_category"] = {"expected": True, "got": set(r["category"] for r in rows) <= set(CATS),
                                        "ok": set(r["category"] for r in rows) <= set(CATS)}
    return {"_about": "สร้างโดย build/dataset_records.py ข้อมูลด้าน dataset เท่านั้น ดูกติกาใน docstring",
            "sources": {k: {"path": v, "sha256": sha(v)} for k, v in sorted(SRC.items())},
            "counts": got, "completeness": comp,
            "names_with_2plus_papers_and_differing_values": dict(conflicts),
            "papers_ir_definition": dict(ir_papers),
            "fields_not_available": {"version": "no separate version field in verified_datasets.csv; variant/version wording, where recorded, is in group_in_paper or preprocessing_note"},
            "checks": checks}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    D, rows = build(); S = summarize(rows)
    bad = [k for k, v in S["checks"].items() if not v["ok"]]
    print(f"checks: {len(S['checks']) - len(bad)}/{len(S['checks'])} ok" + (f"; NOT ok: {bad}" if bad else ""))
    if bad: return 1
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    out = {OUT_CSV: buf.getvalue(), OUT_JSON: json.dumps(S, ensure_ascii=False, indent=1) + "\n"}
    if a.check: return 0
    for path, text in out.items():
        fp = P(path)
        if os.path.exists(fp):
            if open(fp, encoding="utf-8", newline="").read() == text: print(path, "unchanged"); continue
            if not a.overwrite: print(f"STOP: {path} exists with different content; inspect, then rerun with --overwrite"); return 2
        with open(fp, "w", encoding="utf-8", newline="") as fh: fh.write(text)
        print("wrote", path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
