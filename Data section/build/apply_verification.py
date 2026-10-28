"""รวมผลตรวจกับ PDF (18 ต.ค. 2026) เข้ากับข้อมูลรอบอ่านครบ แล้วเขียนไฟล์ที่ใช้เขียน manuscript ได้

อ่าน  out/full_datasets.csv, out/full_outcome_rows.csv   (จาก build/full_extraction.py)
      out/verify_datasets.csv, out/verify_outcomes.csv     (จาก build/verify_pdf.py ตรวจด้วยชั้นข้อความของ PDF)
      out/visual_checks.json                               (Claude เปิดภาพหน้า PDF ดูเองทีละตาราง)
เขียน out/verified_datasets.csv, out/verified_outcomes.csv  เพิ่มคอลัมน์ value_status, verification, verified_page, verified_by
      แผ่นงานใหม่ใน SMOTE25_data_extraction.xlsx: datasets_verified, outcomes_verified (ไม่แตะชีต extraction เดิม)

คำตัดสินของ Toon 18 ต.ค. 22:57: ผลที่ Claude ตรวจนับเป็น verified against paper ได้ แต่ต้องบันทึกว่าใครตรวจ
"""
import csv, json, os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
def rd(f): return list(csv.DictReader(open(f, encoding="utf-8-sig")))
V = json.load(open("out/visual_checks.json", encoding="utf-8"))
def visual(paper, ref, kind):
    for v in V:
        if v["paper"] == paper and v["kind"] == kind and v["ref_sub"] in ref and v["result"] == "ok": return v
    return None
WHO = "Claude, 18 Oct 2026 (counted as verified by Toon's decision)"
def status(st, vis):
    if vis: return "verified against paper", "visual check of rendered PDF page: " + vis["note"][:160]
    if st.startswith("row match on cited page"): return "verified against paper", "PDF text layer: name and values on the same line of the cited page"
    if st.startswith("row match, other page"): return "verified against paper", "PDF text layer: same-line match, page differs from ref"
    if st.startswith("name match"): return "verified against paper", "PDF text layer: name on page, no numbers to check"
    if st.startswith("values on one line"): return "verified against paper", "PDF text layer: both values on one line of the table"
    if st.startswith("ok"): return "verified against paper", "PDF text layer: all values found on the page (prose description)"
    return "not verified", "not found in text layer and no visual check: " + st
def run(full, ver, kind, keyf, reff, out):
    F = rd(full); W = rd(ver); assert len(F) == len(W), (full, len(F), len(W))
    rows = []
    for f, w in zip(F, W):
        assert f[keyf] == w[keyf.replace("dataset", "dataset")] if kind == "outcomes" else f["name"] == w["name"]
        ref = f[reff] if kind == "datasets" else (f["table"] + " " + f["page"])
        vs, how = status(w["status"], visual(f["paper"], ref, kind))
        pg = re.findall(r"@(\d+)", w["detail"]); pg = ("p." + pg[0]) if pg else ""
        rows.append({**f, "value_status": vs, "verification": how, "verified_page": pg, "verified_by": WHO if vs.startswith("verified") else ""})
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    from collections import Counter
    print(out, Counter(r["value_status"] for r in rows))
    return rows
# 19 ต.ค. 2026: verified_outcomes.csv มีการแก้ตามผลตรวจของ Toon (build/apply_outcome_mapping_audit.py) ที่ไฟล์ full_* ต้นทางไม่มี
# ถ้ารันสคริปต์นี้ซ้ำจะเขียนทับการแก้นั้น จึงหยุดไว้ก่อน (ใช้ --force-rebuild ถ้าตั้งใจ แล้วรัน apply_outcome_mapping_audit.py อีกครั้ง)
if "--force-rebuild" not in sys.argv and "mapping_audit" in open("out/verified_outcomes.csv", encoding="utf-8-sig").readline():
    sys.exit("STOP: verified_outcomes.csv carries the 19 Oct mapping audit; rerunning would erase it")
d = run("out/full_datasets.csv", "out/verify_datasets.csv", "datasets", "name", "ref", "out/verified_datasets.csv")
o = run("out/full_outcome_rows.csv", "out/verify_outcomes.csv", "outcomes", "dataset", "page", "out/verified_outcomes.csv")
if "--xlsx" in sys.argv:
    import openpyxl
    wb = openpyxl.load_workbook("SMOTE25_data_extraction.xlsx")
    for name, rows in [("datasets_verified", d), ("outcomes_verified", o)]:
        if name in wb.sheetnames: del wb[name]
        ws = wb.create_sheet(name); cols = list(rows[0]); ws.append(cols)
        for r in rows:
            ws.append([("'" + v) if isinstance(v, str) and v[:1] in "=+-@" and v else v for v in (r[c] for c in cols)])
    wb.save("SMOTE25_data_extraction.xlsx"); print("xlsx sheets written")
