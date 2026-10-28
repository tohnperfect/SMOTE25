"""claim_evidence.py  Analysis F (19 ต.ค. 2026): เงื่อนไขข้อมูลที่ paper ประกาศ เทียบกับข้อมูลที่ใช้ประเมินจริง

เลือก paper: อยู่ในชุดเทียบรายชุด (primary หรือ wrapper, 42 paper) และ "ชื่อเรื่อง" ระบุเงื่อนไขของข้อมูล
  (multi-class, highly/extremely imbalanced หรือ massive, noise/label noise, overlap, difficulty factors) -> 24 paper
  claim = เงื่อนไขที่ชื่อเรื่องระบุ (ข้อความจาก paper_title ใน dataset_records.csv) ไม่ได้อนุมานจากชื่ออัลกอริทึม
หลักฐาน = data entry ที่ผูกกับแถวผลเทียบ SMOTE ของ paper นั้น (out/outcome_dataset_links.csv) + หลักฐานความยาก (out/difficulty_evidence.json)
          + ที่มาของ baseline (out/baseline_provenance_papers.csv)
นิยามป้าย (ระดับเงื่อนไข):
  multi-class   aligned = entry ที่รายงานจำนวนคลาส >= 3 ทุกตัว; partially supported = บางตัว; not aligned = ไม่มีเลย; insufficient = รายงานจำนวนคลาส < ครึ่ง
  high imbalance (เกณฑ์ของการวิเคราะห์นี้ IR ตัวเลขเดี่ยว >= 10; นิยาม IR ต่างกันตาม paper)
                aligned = ทุก entry ที่มี IR ตัวเลข >= 10; partially = บางตัว; not aligned = ไม่มี; insufficient = มี IR ตัวเลข < ครึ่ง
  noise / overlap / difficulty factors
                aligned = มีหลักฐานที่คัดแล้วว่าวัดหรือใส่ภาวะนั้นในการทดลอง; insufficient = ไม่พบในหลักฐานที่คัดแล้ว (ไม่ใช่ "ไม่มี")
  massive       รายงานขนาดแทน (ไม่มีเกณฑ์)
แยกเสมอ: แถวผลเทียบ SMOTE ที่เราสกัดมาจากเงื่อนไขข้อมูลเดิม (ไม่ใส่ noise) ดังนั้นการทดลองเรื่อง noise ไม่ได้อยู่ในชุดเทียบ
"""
import csv, json, os, re, statistics as st
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
D = {r["record_id"]: r for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig"))}
T = {r["paper_key"]: r["paper_title"] for r in D.values()}
O = list(csv.DictReader(open("out/verified_outcomes.csv", encoding="utf-8-sig"))); LK = list(csv.DictReader(open("out/outcome_dataset_links.csv", encoding="utf-8")))
B = {r["paper"]: r for r in csv.DictReader(open("out/baseline_provenance_papers.csv", encoding="utf-8"))}
DF = json.load(open("out/difficulty_evidence.json", encoding="utf-8"))
ev = defaultdict(list)
for i in DF["items"]: ev[i["paper"]].append(i)
COND = [("multi-class", r"multi-?class|multiple classes"), ("high imbalance", r"highly imbalanced|extreme"), ("massive data", r"massive"),
        ("noise", r"nois|label noise"), ("overlap", r"overlap"), ("difficulty factors", r"difficulty factor"), ("binary", r"\bbinary\b")]
def num(x):
    m = re.fullmatch(r"\s*\d[\d,]*(\.\d+)?\s*", x or ""); return float(x.replace(",", "")) if m else None
SEARCHED = {("NROMM", "noise"): "targeted search of main and supplementary text (19 Oct) found no experiment with added or measured noise; its simulated data sets are taken from another paper ([7] in the supplement)"}
rows = []
for k, b in sorted(B.items()):
    if not ("primary" in b["comparison_rows"] or "wrapper" in b["comparison_rows"]): continue
    t = T.get(k, ""); conds = [c for c, p in COND if re.search(p, t, re.I)]
    if not conds or conds == ["binary"]: continue
    recs = {l["record_id"] for o, l in zip(O, LK) if o["paper"] == k and l["record_id"]}
    E = [D[r] for r in recs]
    cls = [num(r["n_classes"]) for r in E]; cls_r = [c for c in cls if c is not None]
    ir = [num(r["ir_as_printed"]) for r in E]; ir_r = [x for x in ir if x is not None]
    ninst = [num(r["n_instances"]) for r in E]; ninst = [x for x in ninst if x is not None]
    for c in conds:
        if c == "binary": continue
        if c == "multi-class":
            m = sum(x >= 3 for x in cls_r)
            lab = "insufficient evidence" if len(cls_r) < len(E) / 2 else ("aligned" if m == len(cls_r) else "partially supported" if m else "not aligned")
            evid = f"{m} of {len(cls_r)} evaluated entries with a class count have >= 3 classes ({len(E) - len(cls_r)} without a class count)"
            if "binary" in conds:   # title claims binary AND multi-class data
                lab = "aligned" if 0 < m < len(cls_r) else lab; evid += "; title names both binary and multi-class data"
        elif c == "high imbalance":
            m = sum(x >= 10 for x in ir_r)
            lab = "insufficient evidence" if len(ir_r) < len(E) / 2 else ("aligned" if m == len(ir_r) else "partially supported" if m else "not aligned")
            evid = f"{m} of {len(ir_r)} entries with a numeric IR have IR >= 10 (range {min(ir_r):g}-{max(ir_r):g}); {len(E) - len(ir_r)} without numeric IR" if ir_r else "no numeric IR"
        elif c == "massive data":
            lab = "reported (no threshold)"; evid = f"instances of evaluated entries: median {st.median(ninst):g}, max {max(ninst):g} (n={len(ninst)})" if ninst else "no sizes"
        else:
            key = {"noise": r"nois", "overlap": r"overlap", "difficulty factors": r"nois|overlap|borderline|disjunct"}[c]
            its = [i for i in ev.get(k, []) if re.search(key, i["property"], re.I)]
            if its:
                lab = "aligned"
                evid = "; ".join(f"{i['type']}: {i['property']} ({i['level'][:60]}; {i['ref']})" for i in its[:3])
            else:
                lab = "insufficient evidence"; evid = SEARCHED.get((k, c)) or "no curated evidence item; keyword passages for this paper not reviewed" if k not in {i["paper"] for i in DF["items"]} else "curated items exist but none for this condition"
        cmp_note = ("comparison rows are from the no-added-noise condition; the noise experiments are not part of the SMOTE pairs"
                    if c == "noise" and lab == "aligned" else "")
        rows.append(dict(paper=k, year=D[next(iter(recs))]["year"] if recs else "", title=t, claimed_condition=c, label=lab, evidence=evid,
                         evaluated_entries=len(E), baseline_provenance=b["provenance"][:2], comparison_rows=b["comparison_rows"], note=cmp_note))
with open("out/claim_evidence_matrix.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
S = dict(selection="papers with per-dataset SMOTE pairs (42) whose title names a data condition", papers=len({r["paper"] for r in rows}),
         claims=len(rows), by_condition={c: dict(Counter(r["label"] for r in rows if r["claimed_condition"] == c)) for c in sorted({r["claimed_condition"] for r in rows})},
         by_label=dict(Counter(r["label"] for r in rows)))
json.dump(S, open("out/claim_evidence_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
for r in rows: print(r["paper"][:14].ljust(14), r["claimed_condition"][:14].ljust(14), r["label"][:22].ljust(22), r["baseline_provenance"], "|", r["evidence"][:120])
