# -*- coding: utf-8 -*-
"""
วิเคราะห์การใช้ dataset ข้าม paper สำหรับ Data section ของ SMOTE25

รันได้สองโหมด
    python3 analyse_dataset_usage.py draft  ai_draft_papers.json   out_dir
    python3 analyse_dataset_usage.py sheet  SMOTE25_data_extraction.xlsx  out_dir

โหมด draft ใช้รายชื่อที่ AI สกัดไว้ ตัวเลขเป็นการสำรวจเบื้องต้นเท่านั้น
โหมด sheet อ่านเฉพาะแถวที่ value_status เป็น verified หรือ corrected จึงเป็นตัวเลขที่อ้างใน paper ได้

ผลลัพธ์เหมือนกันทั้งสองโหมด จะได้เทียบกันได้ว่าตัวเลขขยับไปแค่ไหนหลังตรวจจริง
"""
import sys, re, json, collections, os

# ---------------------------------------------------------------- normalisation
AGG = re.compile(r"(variants?|\bsets\b|^\d+\s|\d+\s+(simulated|artificial|synthetic|KEEL|UCI))", re.I)
RANGE = re.compile(r"\d\s*-\s*\d|\d+\s*to\s*\d+")

def is_aggregate(name):
    """ชื่อที่หมายถึงหลายชุดรวมกัน เช่น 'yeast1-6' หรือ '66 simulated datasets' ขยายไม่ได้"""
    return bool(AGG.search(name) or RANGE.search(name))

def norm(name):
    n = re.sub(r"\([^)]*\)", " ", str(name))
    n = n.strip().lower()
    n = re.sub(r"[_\s]+", " ", n)
    return n.strip()

# ---------------------------------------------------------------- provenance
# จัดเฉพาะชุดที่ยืนยันได้จากการอ่าน paper แล้ว ที่เหลือปล่อยเป็น unclassified
PRIVATE = {
 "oil1","oil2","oil spill","oil spill (9 images, 937 regions)","kr","br",
 "packets","destinations","packets (notre dame)","destinations (notre dame)",
 "prompting","pre2d","prend","compustat","mafalda",
 "sp1","sp3","cccs12","overdue detection database","census-income",
 "internet video traffic","esophageal cancer patients","bearing fault",
 "credit fraud","payment simulation","record linkage","saureus4","acl",
}
SYNTHETIC = {
 "circle","circle (simulated)","checkerboard","checkerboard (synthetic)",
 "art1","art2","art3","art4","subclus","clover","paw",
 "syn-a","syn-b","syn-c","syn-d","syn-e","syn-f","syn-a to syn-f",
 "grid","gridr","ring","alarm","child","asia","insurance",
 "madelon 1","madelon 2","simulated a-d","dsiejdk synthetic family","toy",
}
IMAGE = {
 "mnist","cifar-10","cifar10","svhn","fashion-mnist","lsun","sun397","celeba",
 "celeba-small","celeba-large","lsun-small","lsun-large","ilsvrc-2012 (imagenet)",
 "imagenet8","imagenet9","imagenet12","mnist28","mnist12",
 "samson","jasper ridge","ksc","salinas a","indian pines","ksc (kennedy space center)",
}

def provenance(name):
    n = norm(name)
    if n in PRIVATE:   return "author-collected"
    if n in SYNTHETIC: return "synthetic"
    if n in IMAGE:     return "image benchmark"
    return "unclassified"

# ---------------------------------------------------------------- loaders
def load_draft(path):
    """คืน (rows, meta) โดย rows = [(paper, dataset_name)] และ meta = ข้อมูลระดับ paper"""
    P = json.load(open(path, encoding="utf-8"))
    rows, meta = [], {}
    for p in P:
        meta[p["key"]] = {"nd_claimed": p.get("nd"),
                          "n_listed": len(p.get("dsn") or []),
                          "n_agg": sum(a["count"] for a in (p.get("dsagg") or [])
                                      if not a.get("derived")),
                          "n_agg_entries": len(p.get("dsagg") or []),
                          "sources": p.get("sources") or [], "year": p.get("year")}
        for d in (p.get("dsn") or []):
            rows.append((p["key"], d))
    return rows, meta, "draft"

def load_sheet(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    ex, pp = wb["extraction"], wb["papers"]
    eh = {c.value: i+1 for i, c in enumerate(ex[1])}
    ph = {c.value: i+1 for i, c in enumerate(pp[1])}
    meta = {}
    for r in range(2, pp.max_row+1):
        k = pp.cell(r, ph["method_name"]).value
        if k: meta[k] = {"nd_claimed": pp.cell(r, ph["n_datasets_claimed"]).value,
                         "n_listed": 0, "n_agg": 0, "n_agg_entries": 0,
                         "sources": [], "year": pp.cell(r, ph["year"]).value}
    rows = []
    skipped = 0
    for r in range(2, ex.max_row+1):
        vs = str(ex.cell(r, eh["value_status"]).value or "")
        if not vs.startswith(("verified", "corrected")):
            skipped += 1; continue
        k = ex.cell(r, eh["method_name"]).value
        d = ex.cell(r, eh["dataset_name_as_printed"]).value
        if k and d:
            agg = str(ex.cell(r, eh["is_aggregate"]).value or "").strip().lower() == "yes" \
                  if "is_aggregate" in eh else False
            if agg:
                if k in meta:
                    meta[k]["n_agg"] += int(ex.cell(r, eh["aggregate_count"]).value or 0)
                    meta[k]["n_agg_entries"] += 1
                continue                       # an aggregate row names no dataset
            rows.append((k, d))
            if k in meta: meta[k]["n_listed"] += 1
    print(f"[sheet] ใช้ {len(rows)} แถวที่ตรวจแล้ว ข้าม {skipped} แถวที่ยังไม่ตรวจ")
    return rows, meta, "sheet"

# ---------------------------------------------------------------- analysis
def analyse(rows, meta, mode, outdir):
    singles = [(p, d) for p, d in rows if not is_aggregate(d)]
    aggs    = [(p, d) for p, d in rows if is_aggregate(d)]

    use = collections.defaultdict(set)          # dataset -> {papers}
    printed = collections.defaultdict(set)      # dataset -> {ชื่อที่ paper พิมพ์จริง}
    for p, d in singles:
        use[norm(d)].add(p)
        printed[norm(d)].add(d.strip())

    freq = {k: len(v) for k, v in use.items()}
    dist = collections.Counter(freq.values())

    # ความครบของข้อมูล
    claim  = sum(m["nd_claimed"] or 0 for m in meta.values())
    listed = sum(m["n_listed"] for m in meta.values())
    covagg = sum(m.get("n_agg", 0) for m in meta.values())
    unacc  = sum(max(0, (m["nd_claimed"] or 0) - m["n_listed"] - m.get("n_agg", 0))
                 for m in meta.values())
    short  = sorted((k, (m["nd_claimed"] or 0), m["n_listed"], m.get("n_agg", 0))
                    for k, m in meta.items()
                    if (m["nd_claimed"] or 0) - m["n_listed"] - m.get("n_agg", 0) > 0)
    over   = sorted((k, (m["nd_claimed"] or 0), m["n_listed"], m.get("n_agg", 0))
                    for k, m in meta.items()
                    if m["n_listed"] + m.get("n_agg", 0) - (m["nd_claimed"] or 0) > 0)
    # papers whose headline count rests mostly on entries that name nothing
    heavy = sorted(((m.get("n_agg",0), k, m["nd_claimed"] or 0, m["n_listed"])
                    for k, m in meta.items() if m.get("n_agg",0) > m["n_listed"]
                    and (m["nd_claimed"] or 0) >= m["n_listed"] + m.get("n_agg",0)),
                   reverse=True)

    out = {
      "mode": mode,
      "papers": len(meta),
      "dataset_mentions": len(rows),
      "single_name_mentions": len(singles),
      "aggregate_entries": len(aggs),
      "distinct_datasets": len(freq),
      "claimed_total": claim,
      "listed_total": listed,
      "covered_by_aggregate": covagg,
      "aggregate_entry_count": sum(m.get("n_agg_entries",0) for m in meta.values()),
      "unaccounted": unacc,
      "coverage_pct": round(listed/claim*100, 1) if claim else None,
      "accounted_pct": round((listed+covagg)/claim*100, 1) if claim else None,
      "papers_short": [{"paper": k, "claimed": c, "named": n, "by_aggregate": a,
                        "missing": c-n-a} for k, c, n, a in short],
      "papers_over": [{"paper": k, "claimed": c, "named": n, "by_aggregate": a,
                       "extra": n+a-c} for k, c, n, a in over],
      "aggregate_heavy_papers": [{"paper": k, "claimed": c, "named": n, "by_aggregate": a}
                                 for a, k, c, n in heavy],
      "usage_distribution": {str(k): dist[k] for k in sorted(dist)},
      "core": [], "singletons": [], "aggregates": sorted(set(d for _, d in aggs)),
    }
    for name, n in sorted(freq.items(), key=lambda x: (-x[1], x[0])):
        rec = {"dataset": name, "n_papers": n,
               "printed_as": sorted(printed[name])[:6],
               "provenance": provenance(name),
               "papers": sorted(use[name])}
        if n >= 5: out["core"].append(rec)
        if n == 1: out["singletons"].append(rec)

    prov = collections.Counter(r["provenance"] for r in out["singletons"])
    out["singleton_provenance"] = dict(prov)

    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, f"dataset_usage_{mode}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out

def report(o):
    L = []
    A = L.append
    A(f"โหมด: {o['mode']}   paper: {o['papers']}")
    A(f"dataset mentions ที่เป็นชื่อเดี่ยว : {o['single_name_mentions']}")
    A(f"entry ที่เป็นก้อนรวม ขยายไม่ได้    : {o['aggregate_entry_count']}"
      f"  (ครอบคลุม {o['covered_by_aggregate']} dataset ที่ paper ไม่ได้ตั้งชื่อ)")
    A(f"dataset ที่ต่างกัน                 : {o['distinct_datasets']}")
    if o["coverage_pct"] is not None:
        A(f"ชื่อที่ระบุได้จริง                  : {o['listed_total']} ชื่อ")
        A(f"paper ที่กระทบยอดครบ               : {o['papers']-len(o['papers_short'])} จาก {o['papers']}")
        A(f"ยังค้าง ไม่รู้ว่าเป็น dataset อะไร    : {o['unaccounted']} ชื่อ"
          + ("" if not o["papers_short"] else
             "  (" + ", ".join(f"{h['paper']} {h['missing']}" for h in o["papers_short"]) + ")"))
        if o["papers_over"]:
            A("paper ที่นับได้เกินตัวเลขพาดหัวของตัวเอง:")
            for h in o["papers_over"]:
                A(f"   {h['paper']:<18} พาดหัว {h['claimed']:>3}  แต่ในตารางมี {h['named']+h['by_aggregate']:>3}"
                  f"  (+{h['extra']})")
        if o["aggregate_heavy_papers"]:
            A("")
            A("paper ที่ตัวเลขพาดหัวมาจากก้อนที่ไม่ได้ตั้งชื่อ มากกว่าชื่อที่พิมพ์จริง:")
            for h in o["aggregate_heavy_papers"]:
                A(f"   {h['paper']:<18} อ้าง {h['claimed']:>3}  ตั้งชื่อ {h['named']:>3}  "
                  f"ก้อนรวม {h['by_aggregate']:>3}  = {round(h['by_aggregate']/h['claimed']*100)}% ของพาดหัว")
    A("")
    A("ใช้กี่ paper -> มี dataset กี่ชุด")
    for k, v in o["usage_distribution"].items():
        A(f"   {k:>3s} paper : {v:4d}")
    A("")
    A(f"core (ใช้ตั้งแต่ 5 paper ขึ้นไป): {len(o['core'])} ชุด")
    for r in o["core"][:30]:
        A(f"   {r['n_papers']:3d}  {r['dataset']}")
    A("")
    A(f"singleton (ใช้แค่ paper เดียว): {len(o['singletons'])} ชุด")
    for k, v in sorted(o["singleton_provenance"].items(), key=lambda x: -x[1]):
        A(f"   {k:18s} {v:4d}")
    return "\n".join(L)

if __name__ == "__main__":
    mode, path, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    rows, meta, m = (load_draft if mode == "draft" else load_sheet)(path)
    o = analyse(rows, meta, m, outdir)
    print(report(o))
