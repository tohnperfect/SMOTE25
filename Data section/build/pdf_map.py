"""จับคู่ paper แต่ละเรื่องใน ai-draft/full/ กับไฟล์ PDF ใน paper/ (โฟลเดอร์ที่ Toon ดาวน์โหลดจาก Drive 18 ต.ค.)
เขียน out/pdf_map.json  {key: {"main": path, "supp": [paths]}}
paper/ อยู่ใน .gitignore ห้าม commit
"""
import glob, json, os, re
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)
files = sorted(glob.glob("paper/*/*.pdf"))
base = {os.path.basename(f): f for f in files}
MANUAL = {  # ชื่อไฟล์ในระเบียนไม่ใช่ชื่อจริง ตรวจด้วยมือจากเนื้อหา
}
out = {}
for jf in sorted(glob.glob("ai-draft/full/*.json")):
    key = os.path.basename(jf)[:-5]
    d = json.load(open(jf, encoding="utf-8"))
    txt = str(d.get("pdf_file_read", ""))
    hit = sorted([f for b, f in base.items() if b[:-4] in txt], key=lambda f: -len(f))
    if key in MANUAL: hit = MANUAL[key]
    hit = list(dict.fromkeys(hit))
    main = [h for h in hit if "upplementar" not in h]
    out[key] = {"main": main[0] if main else None, "supp": [h for h in hit if "upplementar" in h], "record": txt[:200]}
json.dump(out, open("out/pdf_map.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items():
    if not v["main"]: print("NO MAIN", k, "|", v["record"][:150])
print("mapped", sum(1 for v in out.values() if v["main"]), "of", len(out))
