"""name_level_extras.py  ตัวเลขที่ตอบ Toon ในแชต 29 ต.ค. 2026 (บ่าย) ให้ย้อนกลับไปหาแหล่งได้ (Claude)
อ่าน  out/name_level_types.csv, out/dataset_records.csv, out/allmetric_links.csv, out/h3_entries.csv, out/pdf_map.json + paper/*.pdf (pdftotext)
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
PRI = ["U-synthetic", "U-minority_mismatch", "U-task_not_reconstructible", "U-size_mismatch", "U-no_printed_size", "U-no_public_file"]
n = R[R.difficulty == "not measured"].copy()
n["reason"] = n.not_measured_reason.map(lambda s: next(x for x in PRI if x in [y.rsplit(" ", 1)[0] for y in s.split("; ")]))
npf = n[n.reason == "U-no_public_file"]
out["not_measured"] = dict(names=int(len(n)), by_reason=n.reason.value_counts().to_dict(),
    no_public_file_by_source=npf.source.value_counts().to_dict(),
    no_public_file_single_paper=int((npf.n_papers.astype(int) == 1).sum()),
    no_public_file_3plus_papers=sorted(npf[npf.n_papers.astype(int) >= 3].normalized_name),
    note="แหล่ง KEEL/UCI/group-level/multiple/other repository = ไฟล์น่าจะมีเผยแพร่แต่ไม่อยู่ใน mirror ที่เข้าถึงได้; private/other paper/not stated = ไม่มีไฟล์ให้ดาวน์โหลด (แบ่งตามแหล่งที่ paper เขียน ยังไม่ได้ตรวจทีละชื่อ)")
pub = npf.source.isin(["KEEL", "UCI", "group-level", "multiple", "other repository"]).sum()
out["not_measured"]["no_public_file_split"] = {"likely_public_not_in_mirror": int(pub), "no_file_to_download": int(len(npf) - pub)}

# 2
m = R[R.mod_ops != ""]
out["modified_ops_per_name"] = dict(names=int(len(m)), by_number_of_ops=dict(sorted(Counter(m.mod_ops.str.count(";") + 1).items())),
                                    combos=dict(Counter(m.mod_ops).most_common()), sum_of_tag_names=int(sum(len(x.split(";")) for x in m.mod_ops)))

# 3  (group, evidence phrase that must occur in the PDF text, file glob)
SYN = {
 "G-SMOTE": ("published", "can be found at https://github.com/IMS-ML-Lab", "*/2019 G-SMOTE*"),
 "GMMSampling": ("published", "the artificial datasets can be found in the repository of multi-imbalance", "*/2024_GMMSampling*"),
 "SVDD-WSMOTE": ("published", "can be found in https://github.com/Zheng7777/simulated-datasets", "*/SVDD-based weighted*"),
 "SMOTE-IPF": ("published", "This web-page also includes the basic information of this paper, the datasets used", "*/SMOTE-IPF*"),
 "SOUP": ("cited source", "synthetic data sets coming from the work of Lango et al. (2017)", "*/2019_SOUP*"),
 "Tomek Links": ("cited source", None, None),
 "NBU": ("code link only", "Source code available at https://github.com/fonkafon/NB-undersampling", "*/2020 NBU*"),
 "DLexiBoost": ("code link only", "Our implementation of LexiBoost can be found at https://github.com/Shounak-D/LexiBoost", "*/DLexiBoost - Boosting*"),
}
NOT = ["ADASYN", "Borderline-SMOTE", "CTGAN / TVAE", "ClusterCentroids", "GOIO", "Global-CS (AAAI)", "Global-CS (journal)", "MWMOTE", "SPE", "SPIDER2", "k-means SMOTE"]
import glob
def txt(g): return re.sub(r"\s+", " ", subprocess.run(["pdftotext", glob.glob("paper/" + g)[0], "-"], capture_output=True, text=True).stdout)
S = D[D.category == "synthetic"]
assert set(S.paper_key) == set(SYN) | set(NOT), f"STOP: synthetic papers changed {set(S.paper_key) ^ (set(SYN) | set(NOT))}"
rows = []
for k, (grp, ev, g) in SYN.items():
    if ev: assert ev in txt(g), f"STOP: evidence phrase not found in PDF for {k}"
    rows.append(dict(paper=k, group=grp, entries=int((S.paper_key == k).sum()), evidence=ev or "ตัวอย่างจาก ref. [4] (บันทึกการอ่าน: Fig. 6 caption p.3)"))
for k in NOT: rows.append(dict(paper=k, group="not found", entries=int((S.paper_key == k).sum()), evidence="ค้นคำ github/http/available/download/supplementary ใน PDF ไม่พบข้อความว่าเผยแพร่ข้อมูล synthetic"))
G = ["published", "cited source", "code link only", "not found"]
out["synthetic_availability"] = dict(papers=len(rows), entries=int(len(S)),
    by_group={x: dict(papers=sum(r["group"] == x for r in rows), entries=sum(r["entries"] for r in rows if r["group"] == x)) for x in G},
    rows=rows, method="pdftotext + ค้นคำ ไม่ได้อ่านทั้งเรื่อง; 'not found' ไม่ได้แปลว่ายืนยันแล้วว่าไม่มี (เช่น CTGAN มี SDGym แต่ PDF ให้ลิงก์เฉพาะข้อมูลจริง)")
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
