"""shuttle_versions.py (19 ต.ค. 2026) ตรวจว่า entry ชื่อ "shuttle" (exact name หลัง normalise) ใช้ version เดียวกันไหม

อ่านเฉพาะค่าที่ตรวจกับ PDF แล้วใน out/dataset_records.csv (ไม่เดา version จากความรู้ภายนอก)
จัดกลุ่ม "printed-metadata group" = entry ที่พิมพ์ n_instances เท่ากัน และ (ถ้าพิมพ์) จำนวน/การกระจายคลาสเข้ากันได้
สถานะ: consistent-in-print = >= 2 paper พิมพ์ขนาดและการกระจายคลาสตรงกัน (ยังไม่ใช่การยืนยันว่าเป็นไฟล์เดียวกัน)
        single-paper / unresolved = มีแค่ paper เดียว หรือขนาดไม่พิมพ์
ไม่รวมกลุ่มต่าง version เข้าด้วยกัน; ชื่อ split (shuttle-c0-vs-c4 ฯลฯ) เป็นชื่ออื่น ไม่อยู่ในไฟล์นี้
เขียน out/shuttle_versions.csv, out/shuttle_versions.json
"""
import csv, json, os, re
from collections import defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
R = [r for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig")) if r["normalized_name"] == "shuttle"]
# ข้อสังเกตที่ตรวจกับ PDF ในรอบนี้ (19 ต.ค.): OVO-SMOTE Table 2 พิมพ์ #Cl. = 5 แต่ Table 3 (p.6) แถว shu มีจำนวนตัวอย่าง 7 คลาส C1-C7 รวม 57,999
PDF_NOTES = {"P024-D017": "paper is internally inconsistent: Table 2 prints 5 classes, Table 3 (p.6) lists 7 class counts summing to 57,999 (checked in PDF 19 Oct)"}
def counts(r):
    return [int(x) for x in re.findall(r"\d+", r["class_distribution"].split("(")[0])] if r["class_distribution"] else []
G = defaultdict(list)
for r in R:
    key = r["n_instances"] or "size not printed:" + r["paper_key"]
    G[key].append(r)
rows, groups = [], []
for i, (k, E) in enumerate(sorted(G.items(), key=lambda x: (x[0].startswith("size"), -len(x[1]), x[0])), 1):
    papers = sorted({r["paper_key"] for r in E})
    dists = {tuple(sorted(counts(r))) for r in E if counts(r)}
    mins = {(r["n_minority"], r["n_majority"]) for r in E if r["n_minority"]}
    ncls = {r["n_classes"] for r in E if r["n_classes"]}
    agree = len(dists) <= 1 and len(mins) <= 1 and len(ncls) <= 1
    if k.startswith("size"): status = "unresolved: size not printed"
    elif len(papers) >= 2 and agree: status = "consistent in print across %d papers (not proof of the same file)" % len(papers)
    elif len(papers) >= 2: status = "same size, class information disagrees: unresolved"
    else: status = "single paper: unresolved"
    gid = f"S{i}"
    groups.append(dict(group=gid, n_instances=("" if k.startswith("size") else k), papers=papers, status=status,
                       n_classes=sorted(ncls), class_counts=[list(d) for d in dists], minority_majority=sorted(mins)))
    for r in E:
        rows.append(dict(group=gid, record_id=r["record_id"], paper_key=r["paper_key"], year=r["year"], name_as_reported=r["name_as_reported"],
                         source_as_reported=r["source_as_reported"], n_instances=r["n_instances"], n_features=r["n_features"], n_classes=r["n_classes"],
                         n_minority=r["n_minority"], n_majority=r["n_majority"], class_distribution=r["class_distribution"], ir_as_printed=r["ir_as_printed"],
                         category=r["category"], category_basis=r["category_basis"], evidence_ref=r["evidence_ref"], group_status=status,
                         pdf_note=PDF_NOTES.get(r["record_id"], ""), preprocessing_note=r["preprocessing_note"]))
with open("out/shuttle_versions.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
S = dict(name="shuttle", entries=len(R), papers=len({r["paper_key"] for r in R}), groups=groups,
         conclusion=("The exact name 'shuttle' covers at least %d different printed versions; they are not pooled. "
                     "No version is confirmed as a specific repository file from paper evidence alone." % sum(1 for g in groups if g["n_instances"])),
         rule="group = identical printed n_instances; status from agreement of printed class counts; no external knowledge used")
json.dump(S, open("out/shuttle_versions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
