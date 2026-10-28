"""Blind re-check of the extracted values (README rule 9; Toon 28 Oct 2026: 15%, dataset characteristics
and per-dataset comparisons with plain SMOTE).

Two modes, run from Data section/:
  python3 build/blind_check.py sample    write blind/blind_sheet.xlsx (no extracted values in it) and
                                         blind/sample_manifest.json (ids, seed, source hashes)
  python3 build/blind_check.py compare   read the filled sheet, compare with out/dataset_records.csv and
                                         out/verified_outcomes.csv, write blind/compare_rows.csv
                                         (one row per checked value, with an empty 'adjudication' column)
                                         and blind/compare_summary.json
  python3 build/blind_check.py summary   after Toon fills 'adjudication', count extraction errors

Sampling: stratified by paper, ceil(15%) of each paper's rows (at least 1), seed 20261028.
  datasets: every named entry (is_placeholder == no) of the 73 papers with an evaluation on data
  outcomes: the primary set, plain SMOTE per-dataset rows without KNNOR's average (541 rows)
Blindness: the sheet gives only where to look (paper, PDF, table, page, row order, the name as printed,
classifier, SMOTE column name). Do not open out/*.csv, the workbook or the Atlas while filling it.
Comparison: values are compared as printed text after normalising (strip spaces and thousands
separators, drop a leading zero, '.8363' == '0.8363', trailing zeros kept apart only if the paper
prints them, so 0.80 vs 0.8 counts as a match with a note); 'NR' = not reported in the paper.
"""
import hashlib, json, math, re, sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
B = HERE / "blind"
SEED, FRAC = 20261028, 0.15
SRC = {"datasets": HERE / "out" / "dataset_records.csv", "outcomes": HERE / "out" / "verified_outcomes.csv"}
DCOLS = ["n_instances", "n_features", "n_classes", "n_minority", "ir_as_printed"]
OCOLS = ["proposed", "smote", "metric"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load():
    d = pd.read_csv(SRC["datasets"], dtype=str).fillna("")
    d = d[d.is_placeholder == "no"].reset_index(drop=True)
    o = pd.read_csv(SRC["outcomes"], dtype=str, encoding="utf-8-sig").fillna("")
    o["row_id"] = ["O%04d" % (i + 1) for i in range(len(o))]  # line order of verified_outcomes.csv
    o = o[(o.smote_kind == "plain SMOTE") & (o.paper != "KNNOR")].reset_index(drop=True)
    if len(o) != 541:
        sys.exit(f"STOP: primary set has {len(o)} rows, expected 541")
    return d, o


def strat(df, key):
    parts = []
    for k, g in df.groupby(key, sort=True):
        n = max(1, math.ceil(FRAC * len(g)))
        parts.append(g.sample(n=n, random_state=SEED))
    return pd.concat(parts).sort_values([key]).reset_index(drop=True)


ALIAS = {"CTGAN / TVAE": "CTGAN", "DSRBF / Static-SMOTE": "DSRBF", "EasyEnsemble / BalanceCascade": "EasyEnsemble",
         "Global-CS (AAAI)": "Global-CS-AAAI", "Global-CS (journal)": "Global-CS-journal", "RACOG / wRACOG": "RACOG",
         "RBBoost / Random Balance": "RBBoost", "ROS (Buda)": "ROS-Buda", "SMOTE-ENN / SMOTE-Tomek": "SMOTE-ENN",
         "Survey: Stop Oversampling": "Stop-Oversampling", "k-means SMOTE": "k-means-SMOTE"}  # paper key -> pdf_map key


def pdf_of(key, pm):
    m = pm.get(key) or pm.get(ALIAS.get(key, ""))
    return m["main"] if m else ""


def sample():
    B.mkdir(exist_ok=True)
    if (B / "blind_sheet.xlsx").exists() and "--force" not in sys.argv:
        sys.exit("STOP: blind/blind_sheet.xlsx exists; it may already hold Toon's answers. Use --force only if it is still empty.")
    d, o = load()
    pm = json.load(open(HERE / "out" / "pdf_map.json", encoding="utf-8"))
    ds, os_ = strat(d, "paper_key"), strat(o, "paper")
    D = pd.DataFrame({"check_id": ["D%03d" % (i + 1) for i in range(len(ds))], "record_id": ds.record_id,
                      "paper": ds.paper_key, "pdf": [pdf_of(k, pm) for k in ds.paper_key], "paper_title": ds.paper_title,
                      "where": ds.characteristics_table_paper.where(ds.characteristics_table_paper != "", ds.evidence_ref),
                      "pdf_page_hint": ds.verified_page, "row_order_in_paper": ds.entry_ordinal_in_paper,
                      "name_as_printed": ds.name_as_reported})
    for c in DCOLS:
        D[c] = ""
    D["note"] = ""
    O = pd.DataFrame({"check_id": ["R%03d" % (i + 1) for i in range(len(os_))], "row_id": os_.row_id, "paper": os_.paper,
                      "pdf": [pdf_of(k, pm) for k in os_.paper], "table": os_.table, "page": os_.page,
                      "pdf_page_hint": os_.verified_page,
                      "dataset_as_printed": os_.dataset_as_printed.where(os_.dataset_as_printed != "", os_.dataset),
                      "classifier": os_.classifier, "smote_column": os_.smote_name})
    for c in ["proposed_method_value", "smote_value", "metric"]:
        O[c] = ""
    O["note"] = ""
    ins = pd.DataFrame({"วิธีกรอก": [
        "1. เปิด PDF ตามคอลัมน์ pdf (โฟลเดอร์ Data section/) ไปที่ตาราง/หน้าที่ระบุ ใช้ row_order และชื่อเพื่อหาแถว",
        "2. ลอกค่าตามที่พิมพ์ใน paper ตรง ๆ ไม่ปัด ไม่แปลง ไม่คำนวณ (เช่น 1,484 / 0.8363 / 1:28.1)",
        "3. ถ้า paper ไม่พิมพ์ค่านั้นเลย ใส่ NR · ถ้าหาแถวไม่เจอหรือกำกวม ใส่ ? แล้วเขียนเหตุผลใน note",
        "4. ห้ามเปิด out/*.csv, workbook หรือ Atlas ระหว่างกรอก (ค่าที่สกัดไว้ไม่อยู่ในไฟล์นี้)",
        "5. datasets: n_instances, n_features, n_classes, n_minority, ir_as_printed (ลอก IR ตามรูปที่พิมพ์ รวมถึง 1: หรือ %)",
        "6. outcomes: ค่าของวิธีที่เสนอ และค่าของ SMOTE ในคอลัมน์ smote_column สำหรับ classifier ที่ระบุ และชื่อ metric ตามที่พิมพ์",
        "7. กรอกเสร็จ บันทึกไฟล์นี้ แล้วรัน python3 build/blind_check.py compare",
        f"สุ่ม {FRAC:.0%} ต่อ paper (อย่างน้อย 1) seed {SEED} · datasets {len(D)} แถว จาก {len(d)} · outcomes {len(O)} แถว จาก {len(o)}"]})
    with pd.ExcelWriter(B / "blind_sheet.xlsx", engine="openpyxl") as w:
        ins.to_excel(w, sheet_name="instructions", index=False)
        D.to_excel(w, sheet_name="datasets", index=False)
        O.to_excel(w, sheet_name="outcomes", index=False)
        for ws in w.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(60, max(10, max(len(str(c.value or "")) for c in col[:40]) + 2))
            ws.freeze_panes = "B2"
    json.dump({"seed": SEED, "frac": FRAC, "datasets": {"n": len(D), "of": len(d), "papers": int(D.paper.nunique()),
                                                       "ids": dict(zip(D.check_id, D.record_id))},
               "outcomes": {"n": len(O), "of": len(o), "papers": int(O.paper.nunique()), "ids": dict(zip(O.check_id, O.row_id))},
               "source_sha256": {k: sha(v) for k, v in SRC.items()}},
              open(B / "sample_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"datasets {len(D)}/{len(d)} rows, {D.paper.nunique()} papers · outcomes {len(O)}/{len(o)} rows, {O.paper.nunique()} papers")


def norm(v):
    s = str(v).strip().replace(" ", "").replace(" ", "").replace(",", "")
    s = s.replace("−", "-")
    if s.upper() in ("NR", "", "NAN", "NONE", "N/A", "-", "NOTREPORTED"):
        return "NR"
    m = re.fullmatch(r"(-?)0*(\d*)(\.\d+)?", s)
    if m and (m.group(2) or m.group(3)):
        ip = m.group(2) or "0"; fp = (m.group(3) or "").rstrip("0").rstrip(".")
        return m.group(1) + ip + fp
    return s.lower()


def wilson(k, n):
    if n == 0:
        return [None, None]
    z = 1.96; p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(max(0, c - h), 4), round(min(1, c + h), 4)]


def compare():
    man = json.load(open(B / "sample_manifest.json", encoding="utf-8"))
    for k, v in SRC.items():
        if sha(v) != man["source_sha256"][k]:
            print(f"WARNING: {v.name} changed since sampling; ids still refer to the same records/lines, check them")
    d, o = load()
    di, oi = d.set_index("record_id"), o.set_index("row_id")
    sh = pd.read_excel(B / "blind_sheet.xlsx", sheet_name=None, dtype=str)
    rows = []
    for _, r in sh["datasets"].fillna("").iterrows():
        rec = di.loc[r.record_id]
        for c in DCOLS:
            rows.append(dict(check_id=r.check_id, kind="dataset", paper=r.paper, item=r.name_as_printed, field=c,
                             toon=r[c], extracted=rec[c], blank=str(r[c]).strip() == ""))
    omap = {"proposed_method_value": "proposed", "smote_value": "smote", "metric": "metric"}
    for _, r in sh["outcomes"].fillna("").iterrows():
        rec = oi.loc[r.row_id]
        for c, src in omap.items():
            rows.append(dict(check_id=r.check_id, kind="outcome", paper=r.paper, item=r.dataset_as_printed, field=src,
                             toon=r[c], extracted=rec[src], blank=str(r[c]).strip() == ""))
    R = pd.DataFrame(rows)
    R["match"] = pd.Series([(norm(a) == norm(b)) if f != "metric" else (str(a).strip().lower() in str(b).lower() or str(b).strip().lower() in str(a).lower())
                  for a, b, f in zip(R.toon, R.extracted, R.field)], dtype=object, index=R.index)
    R.loc[R.blank, "match"] = None
    R["adjudication"] = ""  # after reopening the PDF: extraction_error / checker_error / both_wrong / ambiguous
    R["adjudication_note"] = ""
    R.to_csv(B / "compare_rows.csv", index=False)
    F = R[~R.blank]
    summ = {"filled_values": int(len(F)), "blank_values": int(R.blank.sum())}
    for (kind, field), g in F.groupby(["kind", "field"]):
        k = int((~g.match.astype(bool)).sum())
        summ[f"{kind}:{field}"] = dict(n=int(len(g)), disagree=k, rate=round(k / len(g), 4), ci95=wilson(k, len(g)))
    k = int((~F.match.astype(bool)).sum())
    summ["all"] = dict(n=int(len(F)), disagree=k, rate=round(k / len(F), 4) if len(F) else None, ci95=wilson(k, len(F)))
    json.dump(summ, open(B / "compare_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ["all"]), "· disagreements to adjudicate:", k, "-> blind/compare_rows.csv")


def summary():
    R = pd.read_csv(B / "compare_rows.csv", dtype=str).fillna("")
    F = R[R.blank != "True"]
    dis = F[F.match == "False"]
    if (dis.adjudication == "").any():
        sys.exit(f"STOP: {int((dis.adjudication == '').sum())} disagreements still have no adjudication")
    out = {}
    for (kind, field), g in F.groupby(["kind", "field"]):
        k = int((g.adjudication.isin(["extraction_error", "both_wrong"])).sum())
        out[f"{kind}:{field}"] = dict(n=int(len(g)), extraction_errors=k, rate=round(k / len(g), 4), ci95=wilson(k, len(g)))
    k = int(F.adjudication.isin(["extraction_error", "both_wrong"]).sum())
    out["all"] = dict(n=int(len(F)), extraction_errors=k, rate=round(k / len(F), 4), ci95=wilson(k, len(F)),
                      checker_errors=int((F.adjudication == "checker_error").sum()), ambiguous=int((F.adjudication == "ambiguous").sum()))
    json.dump(out, open(B / "adjudicated_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out["all"]))


if __name__ == "__main__":
    {"sample": sample, "compare": compare, "summary": summary}[sys.argv[1] if len(sys.argv) > 1 else "sample"]()
