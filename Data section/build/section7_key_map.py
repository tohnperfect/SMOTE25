"""จับคู่คีย์ paper ของ Data section กับคีย์ของ Section 7 (draft HTML ของ P)

อ่านอย่างเดียว ../section07-empirical-comparisons-draft.html (ไฟล์ของ P อยู่นอก Data section ห้ามแก้)
อ่าน  SMOTE25_data_extraction.xlsx ชีต papers (method_name, year)
เขียน out/section7_key_map.csv  1 แถวต่อ paper ของเรา 76 แถว

ใช้เพื่อ (1) join ข้อมูลของเรากับของ Section 7 ได้ (2) ใช้ bibkey ชุดเดียวกับทีมใน manuscript
คีย์ของ Section 7 คือคีย์ที่ P ใช้ใน {t:...} และ [[...]] ส่วน bibkey คือคีย์ที่จะเข้า references.bib

รันจาก Data section/:  python3 build/section7_key_map.py
"""
import csv, json, os, re
import openpyxl

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC7 = os.path.join(os.path.dirname(HERE), "section07-empirical-comparisons-draft.html")

# คู่ที่ชื่อต่างกันจนจับอัตโนมัติไม่ได้ ตรวจด้วยมือจากชื่อเรื่องและปี 18 ต.ค. 2026
MANUAL = {
    "ENN (Wilson)": "ENN-1972",
    "Global-CS (AAAI)": "Global-CS-2006",
    "Global-CS (journal)": "Global-CS-2010",
    "ClusterCentroids": "SBC-2009",
    "SMOTE-ENN / SMOTE-Tomek": "SMOTE-ENN-Tomek-2004",
    "EasyEnsemble / BalanceCascade": "EasyEnsemble-BalanceCascade-2009",
    "DSRBF / Static-SMOTE": "DSRBF-2011",
    "RACOG / wRACOG": "RACOG-2015",
    "RBBoost / Random Balance": "RBBoost-2015",
    "ROS (Buda)": "ROS-Buda-2018",
    "k-means SMOTE": "KMeansSMOTE-2018",
    "CTGAN / TVAE": "CTGAN-2019",
    "SVDD-WSMOTE": "SVDDWSMOTE-2022",
    "OREM-M": "OREM-2023",
    "Survey: SMOTE Review": "PradiptaReview-2021",
    "Survey: Stop Oversampling": "StopOversampling-2022",
}

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())

html = open(SEC7, encoding="utf-8").read()
P = json.loads(re.search(r'id="data"[^>]*>(.*?)</script>', html, flags=re.S).group(1))
byk = {p["key"]: p for p in P}
auto = {}
for p in P:
    stem = re.sub(r"-\d{4}$", "", p["key"])
    auto[(norm(stem), int(p["year"]))] = p["key"]

wb = openpyxl.load_workbook(os.path.join(HERE, "SMOTE25_data_extraction.xlsx"), read_only=True)
rows = list(wb["papers"].iter_rows(values_only=True)); h = rows[0]
out, used = [], set()
for r in rows[1:]:
    m = dict(zip(h, r)); name, year = m["method_name"], int(m["year"])
    k = MANUAL.get(name) or auto.get((norm(name), year))
    how = "manual" if name in MANUAL else ("auto" if k else "")
    p = byk.get(k, {})
    if k: used.add(k)
    out.append({"paper_id": m["paper_id"], "data_section_key": name, "year": year,
                "section7_key": k or "", "bibkey": p.get("bibkey", ""), "match": how,
                "section7_empirical": {True: "yes", False: "no"}.get(p.get("empirical"), ""),
                "section7_paper_type": p.get("paper_type", ""), "section7_title": p.get("title", "")})
with open(os.path.join(HERE, "out", "section7_key_map.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
miss = [o["data_section_key"] for o in out if not o["section7_key"]]
print("ours", len(out), "matched", len(out) - len(miss), "unmatched", miss, "section7 keys unused", sorted(set(byk) - used))
