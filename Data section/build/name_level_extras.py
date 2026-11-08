"""name_level_extras.py  ตัวเลขที่ตอบ Toon ในแชต 29 ต.ค. 2026 (บ่าย) ให้ย้อนกลับไปหาแหล่งได้ (Claude)
อ่าน  out/name_level_types.csv, out/dataset_records.csv, out/allmetric_links.csv, out/h3_entries.csv, out/synthetic_availability.json (8 Nov; no PDF needed here any more)
เขียน out/name_level_extras.json
1. not_measured: เหตุที่วัดความยากไม่ได้ ระดับชื่อ (เหตุหลักต่อชื่อตามลำดับ synthetic > minority_mismatch > task_not_reconstructible
   > size_mismatch > no_printed_size > no_public_file) แยกตามแหล่ง
2. modified_ops_per_name: ชื่อหนึ่งถูกดัดแปลงกี่แบบ + ชุด tag ที่พบบ่อย
3. synthetic_availability: paper ที่ใช้ synthetic เผยแพร่ข้อมูลหรือไม่ (Claude อ่านจาก PDF ด้วยการค้นคำ ไม่ได้อ่านทั้งเรื่อง)
   แต่ละ paper มีข้อความยืนยันที่สคริปต์ตรวจว่ามีอยู่จริงใน PDF (หยุดถ้าไม่เจอ) ยกเว้นกลุ่ม "ไม่พบ" ซึ่งไม่มีข้อความให้ยก
4. results_by_type: dataset ที่มีผลเทียบกับ SMOTE ใน paper แยกตามชนิด (ระดับชื่อและ entry)
"""
import json, os, re, subprocess
from collections import Counter
import pandas as pd
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
R = pd.read_csv("out/name_level_types.csv", dtype=str).fillna("")
D = pd.read_csv("out/dataset_records.csv", dtype=str).fillna("")
out = {}

# 1
PRI = ["U-synthetic", "U-minority_mismatch", "U-task_not_reconstructible", "U-name_ambiguous", "U-size_mismatch", "U-no_printed_size", "U-no_class_info", "U-no_public_file"]   # 8 Nov: + name_ambiguous, no_class_info (verify_ext.py)
n = R[R.difficulty == "not measured"].copy()
# 8 Nov second round: a name whose only entries are verifiable but not run (covertype; heart-v with 1 minority row left) -> V-not_run
n["reason"] = n.not_measured_reason.map(lambda s: next((x for x in PRI if x in [y.rsplit(" ", 1)[0] for y in s.split("; ")]), "V-not_run"))
npf = n[n.reason == "U-no_public_file"]
out["not_measured"] = dict(names=int(len(n)), by_reason=n.reason.value_counts().to_dict(),
    no_public_file_by_source=npf.source.value_counts().to_dict(),
    no_public_file_single_paper=int((npf.n_papers.astype(int) == 1).sum()),
    no_public_file_3plus_papers=sorted(npf[npf.n_papers.astype(int) >= 3].normalized_name),
    note="แหล่ง KEEL/UCI/group-level/multiple/other repository = ไฟล์น่าจะมีเผยแพร่แต่ไม่อยู่ใน mirror ที่เข้าถึงได้; private/other paper/not stated = ไม่มีไฟล์ให้ดาวน์โหลด (แบ่งตามแหล่งที่ paper เขียน ยังไม่ได้ตรวจทีละชื่อ)")
pub = npf.source.isin(["KEEL", "UCI", "group-level", "multiple", "other repository"]).sum()
out["not_measured"]["no_public_file_split"] = {"likely_public_not_in_mirror": int(pub), "no_file_to_download": int(len(npf) - pub)}
# 8 Nov 2026: list of names whose paper names a public source but whose file is in none of the mirrors -> for Toon to download
_lp = npf[npf.source.isin(["KEEL", "UCI", "group-level", "multiple", "other repository"])].copy()
_rec = D.set_index("record_id")
def _sizes(ids, col): return "; ".join(sorted({_rec.at[i, col] for i in ids.split("; ") if i in _rec.index and _rec.at[i, col]}))
_lp["printed_n"] = _lp.record_ids.map(lambda x: _sizes(x, "n_instances")); _lp["printed_features"] = _lp.record_ids.map(lambda x: _sizes(x, "n_features"))
_lp["sources_as_reported"] = _lp.record_ids.map(lambda x: _sizes(x, "source_as_reported"))
_lp = _lp.sort_values(["n_papers", "entries", "normalized_name"], ascending=[False, False, True], key=lambda c: c.astype(int) if c.name != "normalized_name" else c)
_lp[["normalized_name", "name_type", "source", "n_papers", "entries", "papers", "printed_n", "printed_features", "sources_as_reported", "record_ids"]].to_csv("out/names_to_download.csv", index=False)
out["not_measured"]["names_to_download"] = dict(file="out/names_to_download.csv", names=int(len(_lp)), by_type=_lp.name_type.value_counts().to_dict(),
    with_printed_size=int((_lp.printed_n != "").sum()))

# 2
m = R[R.mod_ops != ""]
out["modified_ops_per_name"] = dict(names=int(len(m)), by_number_of_ops=dict(sorted(Counter(m.mod_ops.str.count(";") + 1).items())),
                                    combos=dict(Counter(m.mod_ops).most_common()), sum_of_tag_names=int(sum(len(x.split(";")) for x in m.mod_ops)))

# 3  (8 Nov 2026) superseded by build/synthetic_availability.py, which reads every PDF and asserts each quote;
#    the 29 Oct keyword search had missed k-means SMOTE and CTGAN (both publish their simulated data). Copied here.
SA = json.load(open("out/synthetic_availability.json", encoding="utf-8"))
S = D[D.category == "synthetic"]
out["synthetic_availability"] = dict(papers=SA["corpus"]["papers_with_synthetic_entries"], entries=int(len(S)),
    by_group={k: dict(papers=v["papers"], entries=v["entries"]) for k, v in SA["part_A_by_group"].items()},
    rows=[r for r in SA["rows"] if r["part"] == "A"], part_B=SA["part_B"], method=SA["method"], source="out/synthetic_availability.json")
assert sum(v["entries"] for v in out["synthetic_availability"]["by_group"].values()) == len(S)

# 4
L = pd.read_csv("out/allmetric_links.csv", dtype=str).fillna("")
r2n = dict(zip(D.record_id, D.normalized_name)); TY = dict(zip(R.normalized_name, R.name_type))
res = {}
for lab, sub in [("plain_smote", L[(L.record_id != "") & (L.comparator_group == "plain SMOTE")]), ("all_comparators_incl_excluded", L[L.record_id != ""])]:
    names = set(sub.record_id.map(r2n))
    res[lab] = dict(names=len(names), names_by_type=dict(Counter(TY[x] for x in names).most_common()),
                    entries=int(sub.record_id.nunique()), rows=int(len(sub)), rows_by_type=sub.how_obtained.value_counts().to_dict())
H = pd.read_csv("out/h3_entries.csv", dtype=str)
res["h3_listed_entries"] = dict(entries=int(len(H)), in_comparison=int((H.in_comparison == "True").sum()),
                                in_comparison_by_type=H[H.in_comparison == "True"].category.value_counts().to_dict())
out["results_by_type"] = res
json.dump(out, open("out/name_level_extras.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: (v if k != "synthetic_availability" else v["by_group"]) for k, v in out.items()}, ensure_ascii=False, indent=1)[:3500])
