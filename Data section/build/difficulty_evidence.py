"""difficulty_evidence.py  ตรวจและรวมหลักฐานความยากของข้อมูล สำหรับ View C ใน Atlas (เพิ่ม 19 ต.ค. 2026)

อ่าน   ai-draft/difficulty/evidence.json   รายการที่คัดด้วยมือ (Claude อ่านจาก PDF, Toon ยังไม่ได้ตรวจ)
       out/difficulty_candidates.csv       ผลค้นคำ (จาก build/difficulty_candidates.py) ใช้นับจำนวน passage ต่อ paper เท่านั้น
       out/pdf_map.json, PDF ใน paper/     ตรวจ quote และค่าตาราง กับข้อความที่ pdftotext ดึงได้
       out/dataset_records.csv             เชื่อมชื่อ dataset ที่ระบุใน evidence กับ record_id (paper เดียวกัน ชื่อ normalize ตรงกัน)
       out/outcome_dataset_links.csv, out/verified_outcomes.csv, ai-draft/full/*.json  จำนวนแถวผลลัพธ์ต่อ paper และเงื่อนไขที่เลือก
เขียน  out/difficulty_evidence.json
หยุดทำงาน (exit 1) ถ้า quote หรือค่าในตารางข้อใดหาไม่พบในข้อความ PDF  ไม่มีการเดาหรือเติมค่า
"""
import csv, glob, json, os, re, subprocess, sys, unicodedata, hashlib
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE); sys.path.insert(0, os.path.join(HERE, "build"))
from analyse_dataset_usage import norm
import reconcile_counts as RC
PDF2REC = {"CTGAN": "CTGAN / TVAE", "DSRBF": "DSRBF / Static-SMOTE", "EasyEnsemble": "EasyEnsemble / BalanceCascade",
           "Global-CS-AAAI": "Global-CS (AAAI)", "Global-CS-journal": "Global-CS (journal)", "RACOG": "RACOG / wRACOG",
           "RBBoost": "RBBoost / Random Balance", "ROS-Buda": "ROS (Buda)", "SMOTE-ENN": "SMOTE-ENN / SMOTE-Tomek",
           "Stop-Oversampling": "Survey: Stop Oversampling", "k-means-SMOTE": "k-means SMOTE"}
EXTRA = {"MC-RBO": "MC-RBO - Radial-Based Oversampling for Multiclass Imbalanced Data Classification (IEEE TNNLS 2020).pdf"}
def rcsv(f): return list(csv.DictReader(open(f, encoding="utf-8-sig")))
def nz(s):
    s = unicodedata.normalize("NFKC", s).replace("­", "")
    s = re.sub(r"-\s*\n\s*", "-", s)
    s = re.sub(r"[“”\"]", '"', s); s = re.sub(r"[‘’']", "'", s)
    return re.sub(r"\s+", " ", s).strip().lower()
PM = json.load(open("out/pdf_map.json", encoding="utf-8"))
def files(pk):
    if pk not in PM: return []
    f = ([PM[pk]["main"]] if PM[pk]["main"] else []) + list(PM[pk]["supp"])
    return f or ([EXTRA[pk]] if pk in EXTRA else [])
_cache = {}
def pages(path, layout=False):
    k = (path, layout)
    if k not in _cache:
        a = ["pdftotext"] + (["-layout"] if layout else []) + [path, "-"]
        _cache[k] = subprocess.run(a, capture_output=True, text=True, errors="replace").stdout.split("\f")
    return _cache[k]
EV = json.load(open("ai-draft/difficulty/evidence.json", encoding="utf-8"))
D = rcsv("out/dataset_records.csv")
recs = defaultdict(list)
for d in D: recs[d["paper_key"]].append(d)
def link(rk, name):
    n = norm(name)
    hit = [d["record_id"] for d in recs[rk] if d["normalized_name"] == n]
    if not hit: hit = [d["record_id"] for d in recs[rk] if re.sub(r"[^a-z0-9]", "", d["normalized_name"]) == re.sub(r"[^a-z0-9]", "", n)]
    return hit
errors, items = [], []
for i, it in enumerate(EV["items"], 1):
    pk = it["paper"]; rk = PDF2REC.get(pk, pk)
    fl = files(pk); fi = 0 if it["file"] == "main" else 1
    q = nz(it["quote"]); found = []
    if fi < len(fl):
        for pi, t in enumerate(pages(fl[fi]), 1):
            if q in nz(t): found.append(pi)
    if not found: errors.append(f"item {i} {pk}: quote not found: {it['quote'][:70]}")
    out = dict(item_id=f"E{i:03d}", paper=rk, paper_pdf_key=pk, **{k: it[k] for k in ("type", "scope", "property", "level", "measurement", "quote", "ref", "confidence")},
               file=it["file"], quote_found_pdf_pages=found, record_ids=[], dataset_names=it.get("datasets", []), table_values=None)
    for n in it.get("datasets", []):
        ids = link(rk, n)
        if not ids: errors.append(f"item {i} {pk}: dataset '{n}' has no record in the paper")
        out["record_ids"] += ids
    tv = it.get("table_values")
    if tv:
        lay = pages(fl[fi], layout=True)[tv["page"] - 1] if fi < len(fl) else ""
        rows = []
        for name, val in tv["rows"]:
            ok = any(re.match(r"\s*" + re.escape(name) + r"\s", ln) and re.search(r"\s" + re.escape(val) + r"\s*$", ln) for ln in lay.splitlines())
            if not ok: errors.append(f"item {i} {pk}: table row {name}={val} not found on pdf page {tv['page']}")
            ids = link(rk, name)
            rows.append(dict(dataset=name, value=val, record_ids=ids, verified_in_pdf=ok))
        out["table_values"] = dict(page=tv["page"], column=tv["column"], rows=rows)
        out["record_ids"] += [x for r in rows for x in r["record_ids"]]
    items.append(out)
if errors:
    print("\n".join(errors)); sys.exit("STOP: evidence verification failed")
# ---- ระดับ paper ----
CAND = rcsv("out/difficulty_candidates.csv")
cand = Counter(PDF2REC.get(r["paper"], r["paper"]) for r in CAND)
O = rcsv("out/verified_outcomes.csv")
part = defaultdict(Counter)
for o in O:
    if RC.AGG_RE.match(o["dataset"] or ""): k = "excluded"
    elif o["paper"] in {k for k, v in RC.CROSS_TABLE_REVIEW.items() if v.startswith("cross-table")}: k = "excluded"
    elif o["paper"] in RC.EXCLUDED_COMPARATOR: k = "excluded"
    else: k = "primary" if o["smote_kind"] == RC.PLAIN else "wrapper"
    part[o["paper"]][k] += 1
cond = {}
for f in glob.glob("ai-draft/full/*.json"):
    j = json.load(open(f, encoding="utf-8")); c = ((j.get("outcome") or {}).get("chosen") or {})
    cond[j["key"]] = c.get("condition") or ""
papers = []
for rk in sorted({d["paper_key"] for d in D}):
    its = [x for x in items if x["paper"] == rk]
    pk = next((k for k, v in PDF2REC.items() if v == rk), rk)
    types = sorted({x["type"] for x in its})
    papers.append(dict(paper=rk, paper_id=recs[rk][0]["paper_id"], year=recs[rk][0]["year"], n_items=len(its), types=types,
                       status=("curated" if its else ("pdf not available to scan" if not files(pk) else "no curated item (keyword hits not reviewed)")),
                       keyword_passages=cand.get(rk, 0), outcome_rows=dict(part.get(rk, {})), chosen_condition=cond.get(rk, "")))
summ = dict(items=len(items), papers_with_items=sum(p["n_items"] > 0 for p in papers), papers=len(papers),
            by_type=Counter(x["type"] for x in items), by_confidence=Counter(x["confidence"] for x in items),
            papers_by_type={t: sorted({x["paper"] for x in items if x["type"] == t}) for t in EV["types"]},
            records_linked=len({r for x in items for r in x["record_ids"]}), keyword_passages=len(CAND), keyword_papers=len(cand))
sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()
json.dump(dict(about=EV["about"], types=EV["types"], confidence=EV["confidence"], summary=summ, items=items, papers=papers,
               sources={f: sha(f) for f in ["ai-draft/difficulty/evidence.json", "out/difficulty_candidates.csv", "out/dataset_records.csv"]}),
          open("out/difficulty_evidence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summ, ensure_ascii=False, indent=1))
