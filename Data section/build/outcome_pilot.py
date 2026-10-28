"""Pilot: วิธีที่เสนอ เทียบกับ SMOTE รายชุดข้อมูล แยกตามชนิดข้อมูล

อ่าน  ai-draft/outcome/<key>.json        ค่าดิบที่ subagent คัดจากตารางผล (มีตาราง หน้า metric classifier)
      ai-draft/outcome/row_data_type.json ชนิดข้อมูลรายแถว (Claude ให้)
เขียน out/outcome_pilot_rows.csv, out/outcome_pilot_summary.json

ไม่ได้ตัดสินแพ้ชนะตามนิยามของอาจารย์ (ยังไม่ตัดสิน) คอลัมน์ diff = proposed - smote ตามค่าที่พิมพ์
และ raw_sign บอกแค่ว่าค่าที่พิมพ์มากกว่า น้อยกว่า หรือเท่ากัน ยังไม่มีเกณฑ์ tie หรือ significance
รันจาก Data section/:  python3 build/outcome_pilot.py
"""
import csv, glob, json, os, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(HERE, "ai-draft/outcome/row_data_type.json"), encoding="utf-8"))["rows"]

def num(s):
    try: return float(str(s).replace("±", " ").split()[0])
    except Exception: return None

papers, rows = [], []
for f in sorted(glob.glob(os.path.join(HERE, "ai-draft/outcome/*.json"))):
    if f.endswith("row_data_type.json"): continue
    d = json.load(open(f, encoding="utf-8")); c = d.get("chosen", {})
    papers.append(dict(key=d["key"], smote=d.get("smote_in_baselines"), n_rows=len(d.get("rows", [])),
                       metric=c.get("metric"), classifier=c.get("classifier"), table=c.get("table"), page=c.get("page"),
                       granularity="per-dataset" if d.get("rows") else "no per-dataset numbers in paper",
                       summary=d.get("summary_rows", []), claim=d.get("win_claim", {})))
    hib = c.get("higher_is_better", True)
    for r in d.get("rows", []):
        p, s = num(r.get("proposed")), num(r.get("smote"))
        tmap = T.get(d["key"], {})
        dt, why = tmap.get(r["dataset_as_printed"], tmap.get("*", ["unclassified", ""]))
        diff = None if p is None or s is None else round((p - s) if hib else (s - p), 6)
        rows.append(dict(paper=d["key"], dataset=r["dataset_as_printed"], data_type=dt, data_type_basis=why,
                         metric=c.get("metric"), classifier=c.get("classifier"), table=c.get("table"), page=c.get("page"),
                         proposed=r.get("proposed"), smote=r.get("smote"), diff=diff,
                         raw_sign=(None if diff is None else ("+" if diff > 0 else "-" if diff < 0 else "=")),
                         best_other=r.get("best_other_name"), best_other_value=r.get("best_other_value"), marks=r.get("marks")))

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
with open(os.path.join(HERE, "out/outcome_pilot_rows.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def agg(sub):
    ds = [r["diff"] for r in sub if r["diff"] is not None]
    return dict(n=len(sub), proposed_higher=sum(r["raw_sign"] == "+" for r in sub),
                smote_higher=sum(r["raw_sign"] == "-" for r in sub), equal=sum(r["raw_sign"] == "=" for r in sub),
                median_diff=round(st.median(ds), 4) if ds else None, min_diff=min(ds) if ds else None, max_diff=max(ds) if ds else None,
                smote_higher_datasets=[r["dataset"] for r in sub if r["raw_sign"] == "-"])
by = defaultdict(dict)
for k in sorted({r["paper"] for r in rows}):
    sub = [r for r in rows if r["paper"] == k]
    for t in sorted({r["data_type"] for r in sub}):
        by[k][t] = agg([r for r in sub if r["data_type"] == t])
S = dict(_note="pilot 10 paper เลือกแบบเจาะจง ไม่ใช่สุ่ม ค่า diff เป็นหน่วยของ metric ในแต่ละ paper เทียบข้าม paper ไม่ได้ ทุกค่าเป็น ai_draft",
         papers=papers, papers_with_per_dataset=[p["key"] for p in papers if p["n_rows"]],
         papers_without_per_dataset=[p["key"] for p in papers if not p["n_rows"]], by_paper_and_type=by)
json.dump(S, open(os.path.join(HERE, "out/outcome_pilot_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in by.items():
    for t, a in v.items(): print(k, t, a)
