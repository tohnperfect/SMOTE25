"""difficulty_candidates.py  ค้นข้อความใน PDF ที่พูดถึงความยากของข้อมูล (เพิ่ม 19 ต.ค. 2026)

อ่าน  out/pdf_map.json และ PDF ใน paper/ (ไม่อยู่ใน git) ด้วย pdftotext ทีละหน้า
เขียน out/difficulty_candidates.csv  1 แถวต่อประโยคที่มีคำค้น พร้อม paper หน้า (ลำดับหน้าใน PDF) และคำที่เจอ
ไฟล์นี้เป็น "ตัวเลือก" ที่ยังไม่ได้ตีความ การจัดประเภทอยู่ใน ai-draft/difficulty/evidence.json ที่คนอ่านตรวจแล้ว
วิธีรัน (จาก Data section/): python3 build/difficulty_candidates.py   ต้องมี pdftotext (poppler)
"""
import csv, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)
TERMS = re.compile(r"\b(nois\w*|overlap\w*|borderline|small disjunct\w*|disjunct\w*|outlier\w*|label noise|class noise|attribute noise|"
                   r"data scarcity|lack of (?:data|density)|rare (?:case|instance|example)\w*|data difficult\w*|difficulty factor\w*|"
                   r"safe|unsafe|perturb\w*|corrupt\w*|mislabel\w*)\b", re.I)
EXTRA = {"MC-RBO": "MC-RBO - Radial-Based Oversampling for Multiclass Imbalanced Data Classification (IEEE TNNLS 2020).pdf"}
def pages(path):
    out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, errors="replace").stdout
    return out.split("\f")
M = json.load(open("out/pdf_map.json", encoding="utf-8"))
rows = []
for key in sorted(M):
    files = ([M[key]["main"]] if M[key]["main"] else []) + list(M[key]["supp"])
    if not files and key in EXTRA: files = [EXTRA[key]]
    for fi, f in enumerate(files):
        if not os.path.exists(f): continue
        for pi, txt in enumerate(pages(f), 1):
            flat = re.sub(r"\s+", " ", txt)
            for m in TERMS.finditer(flat):
                a, b = max(0, m.start() - 220), min(len(flat), m.end() + 220)
                rows.append(dict(paper=key, file="supplementary" if fi else "main", pdf_page=pi, term=m.group(0).lower(), snippet=flat[a:b].strip()))
# ลดซ้ำ: คำเดียวกันในหน้าเดียวกันที่ snippet ทับกัน เก็บอันแรก
seen, uniq = set(), []
for r in rows:
    k = (r["paper"], r["file"], r["pdf_page"], r["snippet"][:120])
    if k in seen: continue
    seen.add(k); uniq.append(r)
with open("out/difficulty_candidates.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(uniq[0]), lineterminator="\n"); w.writeheader(); w.writerows(uniq)
print("candidates", len(uniq), "papers", len({r["paper"] for r in uniq}))
