"""ตาราง paper x มิติ เรื่องการเลือกและจัดการข้อมูล ทั้ง 76 เรื่อง

อ่าน
  ai-draft/papers.json             ระเบียนรอบ 6 ต.ค. (69 เรื่องมีฟิลด์ระดับ paper ไม่มีเลขหน้า)
  ai-draft/new7/*.json             7 เรื่องที่อ่าน PDF ใหม่ 16 ต.ค. มีเลขหน้าและคำพูดยกมา
  ai-draft/data_handling_codes.json รหัส crit_type / basis / inherited / minority_rule

เขียน
  out/data_handling_matrix.csv     1 แถวต่อ paper พร้อมข้อความต้นทางทุกช่อง เพื่อให้ตรวจย้อนได้
  out/data_handling_summary.json   ตัวนับทุกมิติ ทั้งรวมและแยกช่วงปี

ทุกค่าเป็น ai_draft จนกว่า Toon จะตรวจกับ paper
วิธีรัน (จาก Data section/):  python3 build/data_handling_matrix.py
"""
import csv, glob, json, os
from collections import Counter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(HERE, "ai-draft/papers.json"), encoding="utf-8"))
CODES = json.load(open(os.path.join(HERE, "ai-draft/data_handling_codes.json"), encoding="utf-8"))
NEW = {}
for f in glob.glob(os.path.join(HERE, "ai-draft/new7/*.json")):
    d = json.load(open(f, encoding="utf-8"))
    NEW[d["key"]] = d

def norm_crit_type(s):
    s = (s or "").lower()
    for k in ["own reason", "cites prior work", "generic only", "not stated"]:
        if s.startswith(k):
            return k
    return s or "not stated"

def period(y):
    y = int(y)
    return "1972-2009" if y <= 2009 else ("2010-2019" if y <= 2019 else "2020-2026")

rows = []
for p in P:
    k = p["key"]
    if k in NEW:
        n = NEW[k]; basis, inh, mrule = CODES["codes_new7"][k]
        r = dict(key=k, year=p["year"], task=n.get("task") or p.get("task"),
                 record="new7 (PDF re-read 16 Oct, page refs in ai-draft/new7)",
                 sources=";".join(n.get("sources") or []), origin=";".join(n.get("origin") or []),
                 crit_type=norm_crit_type(n.get("crit_type")), basis=";".join(basis),
                 inherited_from=inh, minority_rule=mrule,
                 src_text=n.get("srcdet", ""), crit_text=n.get("crit", ""),
                 prep_text=n.get("imbalance_creation", ""),
                 quote="; ".join("[p.%s] %s" % (e.get("page"), e.get("quote")) for e in (n.get("evidence") or [])[:3]))
    else:
        ct, basis, inh, mrule = CODES["codes"][k]
        r = dict(key=k, year=p["year"], task=p.get("task"),
                 record="papers.json (6 Oct, no page refs)",
                 sources=";".join(p.get("sources") or []), origin=";".join(p.get("origin") or []),
                 crit_type=ct, basis=";".join(basis), inherited_from=inh, minority_rule=mrule,
                 src_text=p.get("srcdet", ""), crit_text=p.get("crit", ""),
                 prep_text=p.get("prep", ""), quote=p.get("ev", ""))
    r["period"] = period(r["year"])
    r["empirical"] = "no" if r["crit_type"] == "n.a." else "yes"
    r["value_status"] = "ai_draft (unverified)"
    rows.append(r)

cols = ["key", "year", "period", "task", "empirical", "record", "sources", "origin", "crit_type", "basis",
        "inherited_from", "minority_rule", "src_text", "crit_text", "prep_text", "quote", "value_status"]
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
with open(os.path.join(HERE, "out/data_handling_matrix.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

E = [r for r in rows if r["empirical"] == "yes"]
def count(field, subset, multi=False):
    c = Counter()
    for r in subset:
        vals = [v for v in r[field].split(";") if v] if multi else [r[field]]
        c.update(vals or ["(none)"])
    return dict(c.most_common())
def keys(pred, subset):
    return sorted(r["key"] for r in subset if pred(r))

S = {
    "_note": "นับจาก out/data_handling_matrix.csv ทุกค่าเป็น ai_draft ตัวหารคือ paper เชิงประจักษ์ (empirical = yes)",
    "papers_total": len(rows),
    "papers_empirical": len(E),
    "non_empirical": keys(lambda r: r["empirical"] == "no", rows),
    "by_period": dict(Counter(r["period"] for r in E)),
    "crit_type": count("crit_type", E),
    "crit_type_by_period": {pe: count("crit_type", [r for r in E if r["period"] == pe]) for pe in ["1972-2009", "2010-2019", "2020-2026"]},
    "crit_not_stated_or_generic": keys(lambda r: r["crit_type"] in ("not stated", "generic only"), E),
    "basis": count("basis", E, multi=True),
    "inherits_benchmark": keys(lambda r: bool(r["inherited_from"]), E),
    "inherits_wholesale": keys(lambda r: bool(r["inherited_from"]) and not r["inherited_from"].startswith("partial"), E),
    "sources": count("sources", E, multi=True),
    "origin": count("origin", E, multi=True),
    "origin_by_period": {pe: count("origin", [r for r in E if r["period"] == pe], multi=True) for pe in ["1972-2009", "2010-2019", "2020-2026"]},
    "papers_modifying_data": keys(lambda r: any(o in r["origin"] for o in ["Binarised", "Class-merged", "Class-resized", "Undersampled", "Noise-injected", "Induced profile"]), E),
    "papers_generating_data": keys(lambda r: "Generated" in r["origin"], E),
    "minority_rule_all": count("minority_rule", E),
    "minority_rule_among_binarised": count("minority_rule", [r for r in E if "Binarised" in r["origin"]]),
    "binarised_without_stated_rule": keys(lambda r: "Binarised" in r["origin"] and r["minority_rule"] in ("not stated", "not defined"), E),
}
json.dump(S, open(os.path.join(HERE, "out/data_handling_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
