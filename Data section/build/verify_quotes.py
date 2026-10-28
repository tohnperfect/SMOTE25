"""ตรวจว่าประโยคยกมา (quote) ในระดับ paper ของ out/data_handling_matrix.csv มีอยู่จริงใน PDF และอยู่หน้าไหน
เขียน out/verify_quotes.csv  (key, found, page, ratio, quote)
เทียบแบบตัดช่องว่าง/ขีด/ตัวพิมพ์ ยอมความต่างเล็กน้อย (ligature, hyphenation) ด้วย difflib
"""
import csv, json, os, re, glob, difflib
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
FILEKEY = {json.load(open(f, encoding="utf-8"))["key"]: os.path.basename(f)[:-5] for f in glob.glob("ai-draft/full/*.json")}
def norm(t): return re.sub(r"[^a-z0-9]", "", t.lower().replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff"))
out = []
for r in csv.DictReader(open("out/data_handling_matrix.csv", encoding="utf-8-sig")):
    q = (r.get("quote") or "").strip().strip('"').strip("'")
    k = FILEKEY.get(r["key"], r["key"])
    pages = []
    for i in range(0, 3):
        f = os.path.expanduser(f"~/txt/{k}__{i}.json")
        if os.path.exists(f): pages += [(i, n + 1, p) for n, p in enumerate(json.load(open(f))["pages"])]
    if not q or q.lower().startswith("not stated") or not pages:
        out.append({"key": r["key"], "found": "no quote" if not q else ("no pdf text" if not pages else "n/a"), "page": "", "ratio": "", "quote": q}); continue
    # ประโยคยกมามักต่อหลายท่อน (… หรือ ; หรือ [p.x]) จึงตรวจทีละท่อน ท่อนละอย่างน้อย 25 ตัวอักษร
    segs = [norm(x) for x in re.split(r"\[p\.[^\]]*\]|\.\.\.|…|;|(?<=[a-z0-9\)])\.\s", q) if len(norm(x)) >= 25]
    if not segs: segs = [norm(q)]
    hits = []
    for sg in segs:
        hit = None
        for i, n, p in pages:
            if sg in norm(p): hit = (i, n); break
        if not hit:  # ยอมให้ hyphenation / ligature เพี้ยน: หา 30 ตัวแรกหรือ 30 ตัวท้าย
            for i, n, p in pages:
                np_ = norm(p)
                if sg[:30] in np_ or sg[-30:] in np_: hit = (i, n); break
        hits.append(hit)
    ratio = sum(1 for h in hits if h) / len(hits)
    first = next((h for h in hits if h), None)
    best = (ratio, first)
    ok = "exact" if best[0] == 1.0 else ("partial" if best[0] >= 0.5 else "not found")
    pg = "" if not best[1] else (("supp " if best[1][0] else "") + "p." + str(best[1][1]))
    out.append({"key": r["key"], "found": ok, "page": pg, "ratio": round(best[0], 2), "quote": q})
with open("out/verify_quotes.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
from collections import Counter; print(Counter(o["found"] for o in out))
for o in out:
    if o["found"] in ("not found", "partial"): print(o["key"], o["ratio"], o["page"], "|", o["quote"][:150])
