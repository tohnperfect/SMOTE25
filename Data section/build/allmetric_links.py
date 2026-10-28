"""allmetric_links.py  link every all-metric row to a dataset record and its data type (29 Oct 2026, Claude)

Reads  out/winloss_allmetric_rows.csv   (build/winloss_allmetric.py)
       out/verified_outcomes.csv + out/outcome_dataset_links.csv   (rule-A rows, already linked to records)
       out/dataset_records.csv          (1,654 entries; category = how the dataset was obtained)
Writes out/allmetric_links.csv          one row per all-metric row: link method, record_id, how_obtained
       out/allmetric_links_summary.json counts by method

Linking (no judgement, first rule that applies):
  L1 same paper, same printed dataset name as a rule-A row      -> that row's record and how_obtained
  L2 same paper, names equal after dropping a trailing '(...)' and punctuation -> rule-A row
  L3 same paper, exactly one dataset record whose name equals the printed name with 0 or 1 trailing '(...)' removed
  else unmatched (kept, reported apart)
"""
import csv, json, os, re
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)

def rcsv(p, enc="utf-8-sig"): return list(csv.DictReader(open(p, encoding=enc)))
def k1(s): return re.sub(r"\s+", " ", (s or "").strip().lower())
def strip_last_paren(s):
    """drop one trailing balanced parenthetical (handles nested brackets)"""
    s = s.rstrip()
    if not s.endswith(")"): return s
    depth = 0
    for i in range(len(s) - 1, -1, -1):
        depth += {")": 1, "(": -1}.get(s[i], 0)
        if depth == 0: return s[:i].rstrip()
    return s
def k2(s): return re.sub(r"[\s._\-]", "", strip_last_paren(k1(s)))
def kfull(s): return re.sub(r"[\s._\-]", "", k1(s))

W = rcsv("out/winloss_allmetric_rows.csv", "utf-8")
O = rcsv("out/verified_outcomes.csv")
LK = rcsv("out/outcome_dataset_links.csv", "utf-8")
DR = rcsv("out/dataset_records.csv")
CAT = {d["record_id"]: d["category"] for d in DR}
papers_o = sorted({o["paper"] for o in O})
def opaper(p): return next((q for q in papers_o if q == p or q.startswith(p + " /")), None)

by1, by2 = defaultdict(dict), defaultdict(dict)
for o, l in zip(O, LK):
    v = (l["record_id"], o["how_obtained"])
    for nm in {o["dataset"], o.get("dataset_as_printed", "")}:
        if nm: by1[o["paper"]].setdefault(k1(nm), v); by2[o["paper"]].setdefault(k2(nm), v)
rec = defaultdict(lambda: defaultdict(set))
for d in DR:
    for nm in (d["name_as_reported"], d["normalized_name"]):
        if nm:
            rec[d["paper_key"]][kfull(nm)].add(d["record_id"]); rec[d["paper_key"]][k2(nm)].add(d["record_id"])
pkeys = sorted(rec)
def rpaper(p): return next((q for q in pkeys if q == p or q.startswith(p + " /")), None)

out, meth = [], Counter()
for i, r in enumerate(W, 2):
    p, nm = opaper(r["paper"]), r["dataset_as_printed"]
    rid, how, m = "", "unmatched", "unmatched"
    if p and k1(nm) in by1[p]: (rid, how), m = by1[p][k1(nm)], "L1"
    elif p and k2(nm) in by2[p]: (rid, how), m = by2[p][k2(nm)], "L2"
    else:
        rp = rpaper(r["paper"])
        # L3: unique record whose name equals the printed name with zero or one trailing parenthetical removed
        for cand in (kfull(nm), k2(nm)):
            hits = rec[rp].get(cand, set()) if rp else set()
            if len(hits) == 1:
                rid = next(iter(hits)); how, m = CAT.get(rid, "unmatched"), "L3"; break
    if not rid and how != "unmatched": how = how  # rule-A row itself unmatched to a record keeps its label
    meth[m] += 1
    out.append(dict(allmetric_csv_line=i, paper=r["paper"], dataset_as_printed=nm, metric_group=r["metric_group"],
                    comparator_group=r["comparator_group"], result=r["result"], link=m, record_id=rid, how_obtained=how))
with open("out/allmetric_links.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
S = dict(rows=len(out), by_method=dict(meth),
         unmatched_by_paper=dict(Counter(o["paper"] for o in out if o["link"] == "unmatched")),
         plain_by_type=dict(Counter(o["how_obtained"] for o in out if o["comparator_group"] == "plain SMOTE")))
json.dump(S, open("out/allmetric_links_summary.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(S, ensure_ascii=False))
