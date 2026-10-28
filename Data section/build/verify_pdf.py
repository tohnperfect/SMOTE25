"""ตรวจทุกค่าใน out/full_datasets.csv และ out/full_outcome_rows.csv เทียบกับข้อความใน PDF ต้นฉบับ (รอบตรวจ 18 ต.ค. 2026)

วิธี: ดึงข้อความรายหน้าด้วย pdftotext -layout (cache ที่ ~/txt/<key>__<i>.json, i=0 คือ paper, 1.. คือ supplementary)
แล้วหาค่าที่ลอกมาบนหน้าที่อ้าง (ref / page) ยอมหน้าใกล้เคียง ±1 ถ้าไม่เจอค้นทั้งเล่ม
ค่าที่หาไม่เจอในข้อความ = ต้องเปิดดูด้วยตา (ตารางเป็นรูป, ตัวเลขถูกแยกคอลัมน์, หรือค่าผิด)
เขียน out/verify_datasets.csv, out/verify_outcomes.csv, out/verify_summary.json
"""
import csv, json, os, re, collections as C
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
TXT = os.path.expanduser("~/txt")
_cache = {}
import glob
FILEKEY = {json.load(open(f, encoding="utf-8"))["key"]: os.path.basename(f)[:-5] for f in glob.glob("ai-draft/full/*.json")}
def doc(key, i=0):
    key = FILEKEY.get(key, key)
    if (key, i) not in _cache:
        f = f"{TXT}/{key}__{i}.json"
        _cache[(key, i)] = json.load(open(f))["pages"] if os.path.exists(f) else []
    return _cache[(key, i)]
def nums(t): return set(x.replace(",", "").rstrip(".") for x in re.findall(r"\d[\d,]*\.?\d*", t))
def alnum(t): return re.sub(r"[^a-z0-9]", "", t.lower())
def parse_page(ref):
    ref = ref or ""
    sup = 1 if re.search(r"supp|Supplement", ref, re.I) else 0
    m = re.search(r"(?<!printed )(?:main |supp\.? |Supplement[^,]*?, )?p\.\s?(\d+)", ref)
    if "PDF index not determined" in ref: return sup, None
    return sup, int(m.group(1)) if m else None
def numvariants(v):
    v = str(v).strip()
    if v in ("", "None", "null"): return []
    parts = re.findall(r"\d[\d,]*\.?\d*", v)
    out = []
    for p in parts:
        p = p.replace(",", "").rstrip(".")
        alts = {p}
        if "." in p:
            a, b = p.split(".")
            alts.add(a + "." + b.rstrip("0") if b.rstrip("0") else a)
            if a == "0": alts.add("." + b)
        out.append(alts)
    return out
def check(key, sup, page, values, name=None):
    pages = doc(key, sup) or doc(key, 0)
    if not pages: return "no text", {}
    cand = list(range(len(pages)))
    near = [p for p in ([page - 1, page - 2, page] if page else []) if 0 <= p < len(pages)]
    res = {}
    def where(test):
        hit = [p for p in near if test(pages[p])]
        if hit: return "cited", hit[0] + 1
        hit = [p for p in cand if test(pages[p])]
        return ("elsewhere", hit[0] + 1) if hit else ("missing", None)
    if name:
        n = alnum(name)
        res["name"] = where(lambda t: n and n in alnum(t)) if len(n) >= 2 else ("skip", None)
    for f, v in values.items():
        vs = numvariants(v)
        if not vs: continue
        res[f] = where(lambda t: all(any(a in nums(t) for a in alts) for alts in vs))
    # ตรวจระดับแถว: ชื่อกับตัวเลขทุกตัวต้องอยู่บรรทัดเดียวกัน (หรือบรรทัดถัดไป 1 บรรทัดเพราะชื่อยาวขึ้นบรรทัดใหม่ได้)
    # n_classes มักไม่ได้พิมพ์รายแถว (paper บอกครั้งเดียวว่าเป็น 2 คลาส) จึงไม่บังคับให้อยู่บรรทัดเดียวกัน
    allv = [alts for f, v in values.items() if f != "n_classes" for alts in numvariants(v)]
    rowhit = None
    if name and allv:
        n = alnum(name)
        for p in (near + [q for q in cand if q not in near]):
            L = pages[p].splitlines()
            for i, line in enumerate(L):
                if n and n in alnum(line):
                    win = " ".join(L[i:i + 2])
                    ns = nums(win)
                    if all(any(a in ns for a in alts) for alts in allv):
                        rowhit = p + 1; break
            if rowhit: break
    elif not name and allv:  # ผลเทียบ: หาบรรทัดที่มีทั้งค่าของวิธีที่เสนอและ SMOTE
        for p in (near + [q for q in cand if q not in near]):
            for line in pages[p].splitlines():
                ns = nums(line)
                if all(any(a in ns for a in alts) for alts in allv): rowhit = p + 1; break
            if rowhit: break
    res["_row"] = ("row", rowhit) if rowhit else ("norow", None)
    if rowhit: return ("row match on cited page" if rowhit - 1 in near else "row match, other page"), res
    del res["_row"]
    states = [s for s, _ in res.values() if s != "skip"]
    if not states: return "nothing to check", res
    if not allv and res.get("name", ("",))[0] == "cited": return "name match on cited page (no numbers to check)", res
    if not allv and res.get("name", ("",))[0] == "elsewhere": return "name match, other page (no numbers to check)", res
    if all(s == "cited" for s in states): st = "ok on cited page"
    elif all(s in ("cited", "elsewhere") for s in states): st = "ok, other page"
    elif all(s == "missing" for s in states): st = "not in text"
    else: st = "partly missing"
    textless = page and 0 <= page - 1 < len(pages) and len(pages[page - 1].strip()) < 200
    if st != "ok on cited page" and textless: st += " (cited page has no text layer)"
    return st, res

D = list(csv.DictReader(open("out/full_datasets.csv", encoding="utf-8-sig")))
outd = []
for r in D:
    sup, pg = parse_page(r["ref"])
    vals = {f: r[f] for f in ["n_instances", "n_features", "n_classes", "n_minority", "n_majority", "ir_printed"]}
    st, res = check(r["paper"], sup, pg, vals, r["name"] if not r["name"].startswith("[") else None)
    outd.append({**{k: r[k] for k in ["paper", "name", "ref"]}, "status": st,
                 "detail": "; ".join(f"{k}:{s}{'@'+str(p) if p else ''}" for k, (s, p) in res.items())})
O = list(csv.DictReader(open("out/full_outcome_rows.csv", encoding="utf-8-sig")))
outo = []
for r in O:
    sup, pg = parse_page(r["page"] if "p." in (r["page"] or "") else "p." + str(r["page"]))
    st, res = check(r["paper"], sup, pg, {"proposed": r["proposed"], "smote": r["smote"]}, r["dataset"])
    if not st.startswith("row match"):
        st2, res2 = check(r["paper"], sup, pg, {"proposed": r["proposed"], "smote": r["smote"]})
        if st2.startswith("row match"): st, res = "values on one line, name not on that line: " + st2, res2
    outo.append({"paper": r["paper"], "dataset": r["dataset"], "table": r["table"], "page": r["page"],
                 "proposed": r["proposed"], "smote": r["smote"], "status": st,
                 "detail": "; ".join(f"{k}:{s}{'@'+str(p) if p else ''}" for k, (s, p) in res.items())})
for fn, rows in [("out/verify_datasets.csv", outd), ("out/verify_outcomes.csv", outo)]:
    with open(fn, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
S = {"datasets": C.Counter(r["status"] for r in outd), "outcomes": C.Counter(r["status"] for r in outo),
     "datasets_by_paper_not_ok": C.Counter(r["paper"] for r in outd if not r["status"].startswith("ok")),
     "outcomes_by_paper_not_ok": C.Counter(r["paper"] for r in outo if not r["status"].startswith("ok"))}
json.dump(S, open("out/verify_summary.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: dict(v) for k, v in S.items()}, ensure_ascii=False, indent=0))
