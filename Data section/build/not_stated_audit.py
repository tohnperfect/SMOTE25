"""not_stated_audit.py  ตรวจรายการ dataset ที่ category = "not stated" ด้วยหลักฐานข้าม paper ในโปรเจกต์ (เพิ่ม 19 ต.ค. 2026)

อ่าน   out/dataset_records.csv  (ไม่แก้)
เขียน  out/not_stated_audit.csv  1 แถวต่อรายการ not stated  (ไม่เปลี่ยน category เดิม เก็บแยกเป็นคอลัมน์ assessment)

กติกา (เทียบกับ record ของ paper อื่นที่ชื่อ normalize เท่ากัน และ category ไม่ใช่ not stated)
  partial    มี record ใน paper อื่นที่ n_instances และ n_features ตรงกัน (และ n_classes ตรงถ้ามีทั้งสองฝั่ง)
             -> categories_of_matches บอกว่า paper อื่นจัดชุดขนาดเดียวกันไว้ว่าอะไร  ไม่ใช่การยืนยัน
  mismatch   ชื่อนี้มีใน paper อื่น แต่ไม่มี record ใดขนาดตรงกัน (ขนาดต่าง แปลว่าอาจถูกแก้หรือคนละเวอร์ชัน)
  unresolved ชื่อนี้ไม่มีใน paper อื่นที่จัดประเภทแล้ว หรือรายการนี้ไม่มี n_instances/n_features ให้เทียบ
  confirmed  ไม่ใช้ เพราะต้องมีขนาดอ้างอิงจาก repository (KEEL/UCI) ภายนอก ซึ่งไม่มีในข้อมูลโปรเจกต์
"""
import csv, os, re, json
from collections import Counter
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)
D = list(csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig")))
def num(x):
    m = re.search(r"\d[\d,]*(\.\d+)?", x or ""); return m.group(0).replace(",", "") if m else ""
ref = {}
for d in D:
    if d["category"] != "not stated" and d["is_placeholder"] == "no":
        ref.setdefault(d["normalized_name"], []).append(d)
rows = []
for d in D:
    if d["category"] != "not stated": continue
    others = [r for r in ref.get(d["normalized_name"], []) if r["paper_key"] != d["paper_key"]]
    N, F, C = num(d["n_instances"]), num(d["n_features"]), num(d["n_classes"])
    match = [r for r in others if N and F and num(r["n_instances"]) == N and num(r["n_features"]) == F
             and (not C or not num(r["n_classes"]) or num(r["n_classes"]) == C)]
    if not N or not F: st, why = "unresolved", "this entry has no instance or feature count to compare"
    elif not others: st, why = "unresolved", "no other paper reports this normalized name with a stated category"
    elif match: st, why = "partial", f"size matches {len(match)} record(s) in {len({r['paper_key'] for r in match})} other paper(s)"
    else: st, why = "mismatch", f"name reported by {len({r['paper_key'] for r in others})} other paper(s) but none with the same instances/features"
    cats = Counter(r["category"] for r in match)
    rows.append(dict(record_id=d["record_id"], paper_key=d["paper_key"], name_as_reported=d["name_as_reported"], normalized_name=d["normalized_name"],
                     source_as_reported=d["source_as_reported"], n_instances=d["n_instances"], n_features=d["n_features"], n_classes=d["n_classes"],
                     category_paper_reported=d["category"], category_basis=d["category_basis"],
                     assessment=st, assessment_basis=why,
                     categories_of_matches="; ".join(f"{k} {v}" for k, v in cats.most_common()),
                     matching_records="; ".join(r["record_id"] for r in match[:12]),
                     other_records_same_name=len(others), confidence_note="cross-paper consistency only; no external repository reference used"))
with open("out/not_stated_audit.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
c = Counter(r["assessment"] for r in rows)
print("rows", len(rows), dict(c))
print("partial by categories_of_matches:", Counter(r["categories_of_matches"].split(" ")[0] if r["categories_of_matches"] else "" for r in rows if r["assessment"] == "partial"))
print("by paper:", Counter(r["paper_key"] for r in rows).most_common(12))
