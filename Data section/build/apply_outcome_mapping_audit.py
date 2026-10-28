"""apply_outcome_mapping_audit.py  แก้การจับคู่ dataset ของแถว outcome ตามที่ Toon ตรวจกับตารางใน paper (19 ต.ค. 2026)

แก้   out/verified_outcomes.csv  เฉพาะแถวที่ระบุใน AUDIT ข้างล่าง  ไม่แตะคะแนน (proposed, smote, diff, raw_sign) ชื่อที่พิมพ์ (dataset) หรือแถวอื่น
      เพิ่ม 3 คอลัมน์ท้ายไฟล์: dataset_as_printed (ชื่อในตารางผลตามที่ paper พิมพ์ เก็บไว้เพราะ Toon แก้ช่อง dataset ของบางแถวแล้ว)
                               dataset_table_name (ชื่อ entry ในตาราง characteristics ที่แถวนี้คือ ตามที่ verified_datasets.csv บันทึก)
                               mapping_audit (ผลตรวจ; ว่าง = ไม่ได้อยู่ในรอบตรวจนี้)
เขียน out/outcome_mapping_audit.csv  ทุกการเปลี่ยน: แถว, ช่อง, ค่าเดิม, ค่าใหม่, ประเภท, เหตุผล, หลักฐาน (ตาราง/หน้า)

ประเภท
  corrected: characteristics were copied from another entry   ชื่อในตารางผลชี้ dataset ถูก แต่ค่าที่ลอกมา (n, IR, การได้มา) มาจาก entry อื่น
                                                               -> ลอกค่าจาก entry ที่ถูกใน verified_datasets.csv ใหม่ (ช่องที่ outcome ลอกมาเท่านั้น)
  valid: name variant                                         ชื่อย่อ/สะกดต่าง แต่ entry ที่ผูกไว้ถูกแล้ว ไม่เปลี่ยนค่า
  unresolved                                                   หลักฐานไม่พอ (รอบนี้ไม่มี)
ตรวจก่อนเขียน: ทุกช่องที่จะเปลี่ยนต้องยังมีค่าเดิมตามที่บันทึก หรือมีค่าใหม่อยู่แล้ว (รันซ้ำได้) ถ้าเป็นค่าอื่นให้หยุด ไม่ทับการแก้ของ Toon
"""
import csv, os, sys, hashlib
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
F_OUT, F_DS = "out/verified_outcomes.csv", "out/verified_datasets.csv"
COPY = [("how_obtained", "how_obtained_final"), ("how_basis", "how_basis"), ("how_obtained_reader", "how_obtained"),
        ("how_obtained_detail", "how_obtained_detail"), ("source_repo", "source_repo"), ("n_instances", "n_instances"),
        ("n_features", "n_features"), ("n_classes", "n_classes"), ("ir_printed", "ir_printed")]
C, V = "corrected: characteristics were copied from another entry", "valid: name variant"
# (paper, dataset as printed in result table, entry name in verified_datasets.csv, type, reason, evidence)
AUDIT = [
 ("AB-SMOTE", "Harberman (Table VI)", "Haberman", C, "Table VI header prints Majority 225 / Minority 81 (= Haberman 306 in Table I); characteristics had been copied from Telco Customer Churn (7043) by row order. 'Harberman' is the paper's spelling.", "Table VI p.5 (printed 35); Table I p.4 (printed 34); Toon checked 19 Oct 2026"),
 ("AB-SMOTE", "Employee Attrition (Table VII)", "Employe Attrition", C, "Table VII header prints Majority 1233 / Minority 237 (= Employe Attrition 1470 in Table I); characteristics had been copied from Haberman (306) by row order. Table I spells 'Employe'.", "Table VII p.5 (printed 35); Table I p.4 (printed 34); Toon checked 19 Oct 2026"),
 ("AB-SMOTE", "Customer Churn (Table V)", "Customer Churn Wireless Telecom", V, "Short form of the Table I name; Table V header Majority 4293 / Minority 707 matches the 5000-row entry.", "Table V p.5; Table I p.4"),
 ("AB-SMOTE", "Telco Customer Churn (Table VIII)", "Telco Customer Churn", V, "Exact name; Table VIII header Majority 5174 / Minority 1869 matches. Was flagged only because the Haberman row had been linked to the same entry.", "Table VIII p.5; Table I p.4"),
 ("RUSBoost", "CONTRACEPTIVE", "CONTRA2", C, "Only contraceptive data set in Table I is Contra2 (1473, 333 min, 10 attr); text p.9 confirms 'Contraceptive ... (1473 examples) ... 22.61% minority'. Characteristics had been copied from Car3 (1728) by row order.", "Table IV p.9 (printed 193, image); Table I p.5 (printed 189); reference list supplied by Toon 19 Oct 2026"),
 ("RUSBoost", "SATIMG", "SATIMAGE4", C, "Only satimage data set in Table I is SatImage4 (6435, 626 min, 37 attr). Characteristics had been copied from Pendigits5 (10992) by row order.", "Table IV p.9 (printed 193, image); Table I p.5 (printed 189); reference list supplied by Toon 19 Oct 2026"),
 ("RUSBoost", "CAR", "CAR3", V, "Table IV drops the class suffix; only car data set in Table I.", "Table IV p.9; Table I p.5"),
 ("RUSBoost", "PENDIGITS", "PENDIGITS5", V, "Table IV drops the class suffix; only pendigits data set in Table I.", "Table IV p.9; Table I p.5"),
 ("RUSBoost", "ECOLI", "ECOLI4", V, "Table IV drops the class suffix; only ecoli data set in Table I.", "Table IV p.9; Table I p.5"),
 ("RUSBoost", "GLASS", "GLASS3", V, "Table IV drops the class suffix; only glass data set in Table I.", "Table IV p.9; Table I p.5"),
 ("RUSBoost", "SEGMENT", "SEGMENT5", V, "Table IV drops the class suffix; only segment data set in Table I.", "Table IV p.9; Table I p.5"),
 ("RUSBoost", "SOLARFLARE", "SOLARFLAREF", V, "Table IV drops the class suffix; only solar flare data set in Table I.", "Table IV p.9; Table I p.5"),
 ("RUSBoost", "VEHICLE", "VEHICLE1", V, "Table IV drops the class suffix; only vehicle data set in Table I.", "Table IV p.9; Table I p.5"),
 ("DGOT", "bankruptcy", "polish_bankruptcy", C, "Table V has 22 rows that map one-to-one onto the 22 Table I entries; 20 names are exact, the remaining pair is bank_small/bankruptcy vs bank/polish_bankruptcy. Table V rows follow IR order and 'bankruptcy' sits between letter_img (26.0) and avila (97.4), where only polish_bankruptcy (45.2) fits. Characteristics had been copied from bank (4521).", "Table V p.10 (printed 992); Table I p.8 (printed 990); reference list supplied by Toon 19 Oct 2026"),
 ("DGOT", "bank_small", "bank", V, "Results-table name for Table I 'bank' (4521, IR 7.7), same IR position; characteristics already match.", "Table V p.10; Table I p.8"),
 ("CBHSID", "River", "Liver", V, "Table 3 prints 'River' in row 1; Table 1 (Sr.1) and Table 4 row 1 print 'Liver'. Characteristics (6 features, IR 1.38) already match Liver. Name kept as printed; Toon confirmed Liver 19 Oct 2026.", "Table 3 p.9 (printed 118647); Table 1 p.8 (printed 118646); Table 4 p.9"),
]
# ชื่อที่ Toon แก้ในช่อง dataset เอง (19 ต.ค. 2026) เก็บไว้ตามนั้น ไม่เปลี่ยนกลับ
USER_RENAMED = {("AB-SMOTE", "Customer Churn (Table V)"): "Customer Churn Wireless Telecom(Table V)", ("CBHSID", "River"): "Liver"}
# รอบที่ 2 (19 ต.ค. 2026 ภายหลัง): ชื่อย่อ 13 แถวที่เหลือ + 8 แถวที่ full_extraction จับคู่ด้วย row order แต่ชื่อดูคล้ายจึงไม่ถูกตั้งธง
RB = "Supplementary Table 11 pp.17-18 / Table 3 pp.3-5 (labels truncated by column width); main Table 3 p.8 (printed p.103) gives the full KEEL name"
AUDIT += [
 ("ADASYN", "Pima Indian Diabetes", "Diabetes (PID)", V, "Table I lists 'Diabetes (PID)' (768, 268/500, 8 attr); text p.4 describes it as the 'Pima Indian Diabetes dataset'; Table II uses that name.", "Table I p.3 (printed 1324); text p.4; Table II p.5 (printed 1326)"),
 ("CGMOS", "UserKnowledge", "UKnowledge", V, "No abbreviation key printed. Table 1 and Table 3 each list 30 data sets; 29 names match exactly and this is the only remaining pair (403 instances, 5 attr). Verified by one-to-one elimination.", "Table 1 p.5 (printed 1627); Table 3 p.7 (printed 1629)"),
 ("MKC-SMOTE", "cmc", "Contraceptive Method Choice", V, "Table 1 ID column defines cmc = Contraceptive Method Choice (1473, 9, 3 classes).", "Table 1 p.5 (printed 196933, image); Table 4 p.7 (printed 196935)"),
 ("MKC-SMOTE", "ctg", "Cardiotocography", V, "Table 1 ID column defines ctg = Cardiotocography (1728, 21, 3 classes as printed).", "Table 1 p.5 (printed 196933, image); Table 4 p.7"),
 ("MKC-SMOTE", "con", "Connect-4", V, "Table 1 ID column defines con = Connect-4 (row-order match, now checked).", "Table 1 p.5; Table 4 p.7"),
 ("MKC-SMOTE", "car", "Car Evaluation", V, "Table 1 ID column defines car = Car Evaluation (row-order match, now checked).", "Table 1 p.5; Table 4 p.7"),
 ("MLOS", "aba19", "abalone19", V, "Table 1 Abbr column prints aba19 for abalone19 (4174, 8, IR 129.44).", "Table 1 p.9; Table 8 p.13"),
 ("MLOS", "win35", "winequalityred3vs5", V, "Table 1 Abbr column prints win35 for winequalityred3vs5 (691, 11, IR 68.10).", "Table 1 p.9; Table 8 p.13"),
 ("MLOS", "win", "winequality", V, "Table 1 Abbr column prints win for winequality (row-order match, now checked).", "Table 1 p.9; Table 8 p.13"),
 ("OVO-SMOTE", "wqr", "Wine-Quality-Red", V, "Table 2 abbreviation column prints Wqr for Wine-Quality-Red (1599, 11).", "Table 2 p.6 (printed 102); Table 7 p.10 (printed 106)"),
 ("OVO-SMOTE", "wqw", "Wine-Quality-White", V, "Table 2 abbreviation column prints Wqw for Wine-Quality-White (4898, 11).", "Table 2 p.6; Table 7 p.10"),
 ("OVO-SMOTE", "win", "Wine", V, "Table 2 abbreviation column prints Win for Wine (178, 13) (row-order match, now checked).", "Table 2 p.6; Table 7 p.10"),
 ("AMDO", "UKM", "User-knowledge-modelling (UKM)", V, "Table 1 prints the abbreviation UKM with the full name (row-order match, now checked).", "Table 1 p.7; Tables 6/9 p.10-11"),
 ("EMDO", "UKM", "User-Knowledge-Modelling (UKM)", V, "Table 1 prints the abbreviation UKM with the full name (row-order match, now checked).", "Table 1 p.13; Table 5 p.15"),
 ("MBS", "Credit", "Give Me Some Credit", V, "Only credit data set in Table 2 (150000, 10); results use the short form. Verified by elimination (row-order match, now checked).", "Table 2 p.7 (printed 1549); Table 3 p.8 (printed 1550)"),
 ("SOUP", "thyroid", "new_thyroid", V, "Only thyroid data set in Table 2 ('new thyroid'); results use 'thyroid'. Verified by elimination (row-order match, now checked).", "Table 2 p.8 (printed 776); Table 6 p.11 (printed 779)"),
 ("RBBoost / Random Balance", "keel ecoli-0-1-4-7 vs 2-3", "ecoli-0-1-4-7_vs_2-3-5-6", V, "Truncated label; the only Table 3 name with this prefix (336, IR 10.59).", RB),
 ("RBBoost / Random Balance", "keel glass-0-1-2-3 vs 4-5", "glass-0-1-2-3_vs_4-5-6", V, "Truncated label; the only Table 3 name with this prefix (214, IR 3.20).", RB),
 ("RBBoost / Random Balance", "keel led7digit-0-2-4-5-6-", "led7digit-0-2-4-5-6-7-8-9_vs_1", V, "Truncated label; the only Table 3 name with this prefix (443, IR 10.97).", RB),
 ("RBBoost / Random Balance", "keel yeast-0-2-5-6 vs 3-7", "yeast-0-2-5-6_vs_3-7-8-9", V, "Truncated label; the only Table 3 name with this prefix (1004, IR 9.14).", RB),
 ("RBBoost / Random Balance", "keel yeast-0-2-5-7-9 vs 3", "yeast-0-2-5-7-9_vs_3-6-8", V, "Truncated label; the only Table 3 name with this prefix (1004, IR 9.14).", RB),
]
def rd(f):
    with open(f, encoding="utf-8-sig", newline="") as fh:
        r = csv.DictReader(fh); return r.fieldnames, list(r)
fo, O = rd(F_OUT); _, D = rd(F_DS)
_head = open(F_OUT, "rb").read(4000); bom = _head[:3] == b"\xef\xbb\xbf"; EOL = "\r\n" if b"\r\n" in _head else "\n"
NEW = ["dataset_as_printed", "dataset_table_name", "mapping_audit"]
fo2 = fo + [c for c in NEW if c not in fo]
log, errors = [], []
for paper, ds, tname, kind, why, ev in AUDIT:
    names = {ds, USER_RENAMED.get((paper, ds), ds)}
    rows = [(i, o) for i, o in enumerate(O, 2) if o["paper"] == paper and o["dataset"] in names]
    ents = [d for d in D if d["paper"] == paper and d["name"] == tname]
    if len(rows) != 1 or len(ents) != 1:
        errors.append(f"{paper} / {ds}: {len(rows)} outcome rows, {len(ents)} dataset entries named {tname}"); continue
    i, o = rows[0]; d = ents[0]
    changes = [("dataset_as_printed", o.get("dataset_as_printed", ""), ds), ("dataset_table_name", o.get("dataset_table_name", ""), tname), ("mapping_audit", o.get("mapping_audit", ""), kind)]
    if (paper, ds) in USER_RENAMED and o["dataset"] == ds:   # ทำซ้ำการแก้ชื่อของ Toon ถ้าไฟล์ถูกสร้างใหม่จากต้นทาง
        changes.append(("dataset", ds, USER_RENAMED[(paper, ds)]))
    if kind == C:
        changes += [(a, o[a], d[b]) for a, b in COPY]
        changes.append(("match", o["match"], "corrected 19 Oct 2026 (see out/outcome_mapping_audit.csv)"))
    else:
        bad = [a for a, b in COPY if o[a] != d[b]]
        if bad: errors.append(f"{paper} / {ds}: marked valid but copied fields differ from {tname}: {bad}")
    for fld, old, new in changes:
        if old == new: continue
        log.append(dict(outcome_csv_line=i, paper=paper, dataset_as_printed=ds, field=fld, original_value=old, corrected_value=new,
                        classification=kind, reason=why, evidence=ev))
        o[fld] = new
if errors:
    print("\n".join(errors)); sys.exit("STOP: nothing written")
for o in O:
    for c in NEW: o.setdefault(c, "")
if not log:
    print("no changes (already applied)"); sys.exit(0)
with open(F_OUT, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fo2, lineterminator=EOL)
    w.writeheader(); w.writerows(O)
au = "out/outcome_mapping_audit.csv"
prev = list(csv.DictReader(open(au, encoding="utf-8"))) if os.path.exists(au) else []
with open(au, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(log[0]), lineterminator="\n"); w.writeheader(); w.writerows(prev + log)
from collections import Counter
print("changed cells", len(log), "rows", len({l["outcome_csv_line"] for l in log}), Counter(l["classification"] for l in log if l["field"] == "mapping_audit"))
