"""outcome_links.py  เชื่อมแถว outcome กับ record_id ของ dataset (เพิ่ม 19 ต.ค. 2026)

อ่าน  out/verified_outcomes.csv (835 แถว) และ out/dataset_records.csv (1,654 แถว)  ไม่แก้ไฟล์ทั้งสอง
เขียน out/outcome_dataset_links.csv  1 แถวต่อแถว outcome (ลำดับเดียวกับไฟล์ต้นทาง)

วิธีเชื่อม (deterministic ไม่มีการเดา)
 1. ผู้สมัคร = record ใน paper เดียวกันที่ค่าซึ่งถูกลอกมาตอนสร้างตาราง outcome ตรงกันทุกช่อง
    (how_obtained_detail = preprocessing_note, source_repo = source_as_reported, n_instances, n_features, n_classes,
     ir_printed = ir_as_printed)
 2. ผู้สมัคร 1 รายการ -> link_method "fields"
 3. หลายรายการ -> เลือกที่ชื่อ normalize ตรงกับชื่อใน outcome ถ้าเหลือ 1 -> "fields+name"
    ถ้ายังเหลือหลายรายการและทุกรายการมี n/f/c/ir เท่ากัน -> เลือกรายการแรกตามลำดับใน paper และบันทึก "fields+name (duplicate entries)"
 4. ไม่มีผู้สมัคร หรือแถว outcome เป็น unmatched/aggregate -> ไม่ link (record_id ว่าง) และบอกเหตุผล
ค่าลักษณะ dataset ที่ View B ใช้ อ่านจาก record ที่ link ได้เท่านั้น ไม่เติมค่าแทน
"""
import csv, os, re, sys, json, hashlib
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE); sys.path.insert(0, os.path.join(HERE, "build"))
from analyse_dataset_usage import norm
def rcsv(f): return list(csv.DictReader(open(f, encoding="utf-8-sig")))
O, D = rcsv("out/verified_outcomes.csv"), rcsv("out/dataset_records.csv")
PAIRS = [("how_obtained_detail", "preprocessing_note"), ("source_repo", "source_as_reported"), ("n_instances", "n_instances"),
         ("n_features", "n_features"), ("n_classes", "n_classes"), ("ir_printed", "ir_as_printed")]
RN = {d["record_id"]: d["name_as_reported"] for d in D}
by_paper = {}
for d in D: by_paper.setdefault(d["paper_key"], []).append(d)
out, used = [], {}
for i, o in enumerate(O, 2):
    cand = [d for d in by_paper.get(o["paper"], []) if all((o[a] or "").strip() == (d[b] or "").strip() for a, b in PAIRS)]
    rid, meth, note = "", "", ""
    if o["match"] == "unmatched":
        meth, note = "not linked", "outcome row marked unmatched in source"
    elif not cand:
        meth, note = "not linked", "no record in the same paper with identical copied fields"
    elif len(cand) == 1:
        rid, meth = cand[0]["record_id"], "fields"
    else:
        nm = [d for d in cand if d["normalized_name"] == norm(o["dataset"])]
        if len(nm) == 1: rid, meth = nm[0]["record_id"], "fields+name"
        elif len(nm) > 1: rid, meth, note = nm[0]["record_id"], "fields+name (duplicate entries)", "; ".join(d["record_id"] for d in nm)
        else: meth, note = "not linked", f"{len(cand)} records share the copied fields, none with the same name: " + "; ".join(d["record_id"] for d in cand)
    if rid: used[rid] = used.get(rid, 0) + 1
    out.append(dict(outcome_csv_line=i, paper=o["paper"], dataset=o["dataset"], outcome_match=o["match"], smote_kind=o["smote_kind"],
                    raw_sign=o["raw_sign"], record_id=rid, record_name=RN.get(rid, ""), link_method=meth, link_note=note))
# ตรวจความสอดคล้องของชื่อ (ไม่เปลี่ยน link แค่ติดธง)
# name_check = agrees   ชื่อ outcome กับ record ตรงกันเมื่อเทียบเฉพาะตัวอักษรและตัวเลข (ตัวหนึ่งอยู่ในอีกตัว รวมข้อความในวงเล็บ)
#            = differs  ไม่ตรง และแถว outcome ถูกจับคู่ด้วย row order/prefix หรือ record เดียวถูกใช้โดย outcome คนละชื่อ
#            = notation ไม่ตรงตัวอักษร แต่ source จับคู่ด้วย name (เช่น ตัวย่อ 'ldd1 (abalone7)', 'Seg.' กับ 'Segment')
def an(x): return re.sub(r"[^a-z0-9]", "", x.lower())
def agrees(a, b):
    A = [an(a)] + [an(t) for t in re.findall(r"\(([^)]*)\)", a)]
    B = an(b)
    return any(x and B and (x in B or B in x) for x in A)
names_per_rec = {}
for r in out:
    if r["record_id"]: names_per_rec.setdefault(r["record_id"], set()).add(an(re.sub(r"\([^)]*\)", "", r["dataset"])))
for r in out:
    if not r["record_id"]: r["name_check"] = ""; continue
    tn = (O[r["outcome_csv_line"] - 2].get("dataset_table_name") or "").strip()
    if tn:   # แถวที่ตรวจแล้ว (build/apply_outcome_mapping_audit.py): เทียบกับชื่อ entry ที่ตรวจแล้ว
        r["name_check"] = "agrees (audited)" if tn == r["record_name"] else "differs"; continue
    shared = len(names_per_rec[r["record_id"]]) > 1
    if agrees(r["dataset"], r["record_name"]) and not shared: r["name_check"] = "agrees"
    elif r["outcome_match"] == "name" and not shared: r["name_check"] = "notation"
    else: r["name_check"] = "differs"
with open("out/outcome_dataset_links.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out)
from collections import Counter
print("rows", len(out), Counter(r["link_method"] for r in out))
print("records linked by >1 outcome row:", sum(v > 1 for v in used.values()))
print("name_check", Counter(r["name_check"] for r in out))
for r in out:
    if r["name_check"] == "differs": print("  differs:", r["paper"], "|", r["dataset"], "->", r["record_id"], r["record_name"], "|", r["outcome_match"])
for r in out:
    if r["link_method"] == "not linked": print(" ", r["paper"], "|", r["dataset"], "|", r["outcome_match"], "|", r["link_note"][:90])
